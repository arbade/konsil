#!/usr/bin/env python3
"""Build the standard Konsil viewer for a scene directory.

Reads <scene>/structures.json (produced by dicom_to_scene.py), maps every
TotalSegmentator structure name to a Turkish label / anatomical group / color,
writes <scene>/scene.json and copies the shared viewer template so every case
gets the exact same viewer. Deterministic; no AI touches pixels.

Usage:
  python build_scene_viewer.py <scene_dir> --title "Konsil — Abdomen BT (23.05.2026)" \
      [--volume "Etiket=nifti/volume.nii.gz" ...]

If no --volume is given, nifti/*.nii.gz are auto-detected (labeled by filename).
"""
import argparse, json, re, shutil
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "skills" / "imaging-3d" / "assets" / "viewer.html"

# name -> (turkish label, group, rgba, default-on)
ORG, SOL, DAM, KEM, KAS = "Organlar", "Solunum", "Damarlar", "Kemik", "Kas"
STRUCTURES = {
    # abdominal / urogenital organs
    "liver":                ("Karaciğer", ORG, (150, 90, 60, 220), True),
    "spleen":               ("Dalak", ORG, (120, 60, 120, 220), True),
    "stomach":              ("Mide", ORG, (220, 150, 110, 220), True),
    "pancreas":             ("Pankreas", ORG, (220, 180, 140, 230), True),
    "gallbladder":          ("Safra kesesi", ORG, (100, 180, 100, 230), True),
    "kidney_right":         ("Sağ böbrek", ORG, (220, 80, 80, 255), True),
    "kidney_left":          ("Sol böbrek", ORG, (240, 140, 60, 255), True),
    "kidney_cyst_right":    ("Sağ böbrek kisti", ORG, (250, 240, 120, 255), True),
    "kidney_cyst_left":     ("Sol böbrek kisti", ORG, (250, 250, 160, 255), True),
    "adrenal_gland_right":  ("Sağ sürrenal", ORG, (240, 200, 60, 255), True),
    "adrenal_gland_left":   ("Sol sürrenal", ORG, (240, 220, 100, 255), True),
    "urinary_bladder":      ("Mesane", ORG, (80, 140, 220, 255), True),
    "prostate":             ("Prostat", ORG, (160, 100, 200, 255), True),
    "spinal_cord":          ("Omurilik", ORG, (230, 230, 160, 255), False),
    "brain":                ("Beyin", ORG, (210, 170, 170, 230), False),
    "thyroid_gland":        ("Tiroid", ORG, (200, 120, 90, 255), False),
    "heart":                ("Kalp", ORG, (190, 50, 70, 240), False),
    "esophagus":            ("Özofagus", ORG, (200, 160, 120, 230), False),
    "small_bowel":          ("İnce bağırsak", ORG, (215, 170, 130, 180), False),
    "duodenum":             ("Duodenum", ORG, (205, 150, 105, 210), False),
    "colon":                ("Kolon", ORG, (180, 140, 100, 180), False),
    # respiratory
    "trachea":              ("Trakea", SOL, (170, 210, 230, 230), False),
    "lung_upper_lobe_left": ("Sol akciğer üst lob", SOL, (235, 160, 160, 170), False),
    "lung_lower_lobe_left": ("Sol akciğer alt lob", SOL, (220, 130, 130, 170), False),
    "lung_upper_lobe_right": ("Sağ akciğer üst lob", SOL, (240, 170, 150, 170), False),
    "lung_middle_lobe_right": ("Sağ akciğer orta lob", SOL, (230, 150, 140, 170), False),
    "lung_lower_lobe_right": ("Sağ akciğer alt lob", SOL, (215, 125, 120, 170), False),
    # vessels
    "aorta":                ("Aort", DAM, (200, 40, 40, 255), True),
    "inferior_vena_cava":   ("Vena kava inferior", DAM, (60, 60, 200, 230), True),
    "superior_vena_cava":   ("Vena kava superior", DAM, (70, 80, 210, 230), False),
    "portal_vein_and_splenic_vein": ("Portal + splenik ven", DAM, (90, 110, 220, 230), True),
    "iliac_artery_left":    ("Sol iliyak arter", DAM, (210, 60, 60, 240), False),
    "iliac_artery_right":   ("Sağ iliyak arter", DAM, (210, 60, 60, 240), False),
    "iliac_vena_left":      ("Sol iliyak ven", DAM, (80, 90, 210, 230), False),
    "iliac_vena_right":     ("Sağ iliyak ven", DAM, (80, 90, 210, 230), False),
    "pulmonary_vein":       ("Pulmoner ven", DAM, (110, 120, 220, 230), False),
    "brachiocephalic_trunk": ("Brakiosefalik trunkus", DAM, (200, 70, 60, 240), False),
    "brachiocephalic_vein_left": ("Sol brakiosefalik ven", DAM, (90, 100, 215, 230), False),
    "brachiocephalic_vein_right": ("Sağ brakiosefalik ven", DAM, (90, 100, 215, 230), False),
    "common_carotid_artery_left": ("Sol ana karotis", DAM, (205, 65, 60, 240), False),
    "common_carotid_artery_right": ("Sağ ana karotis", DAM, (205, 65, 60, 240), False),
    "subclavian_artery_left": ("Sol subklavyen arter", DAM, (205, 70, 65, 240), False),
    "subclavian_artery_right": ("Sağ subklavyen arter", DAM, (205, 70, 65, 240), False),
    "atrial_appendage_left": ("Sol atriyal apendiks", DAM, (190, 80, 90, 240), False),
    # bone
    "skull":                ("Kafatası", KEM, (222, 214, 190, 235), False),
    "sternum":              ("Sternum", KEM, (222, 214, 190, 235), False),
    "sacrum":               ("Sakrum", KEM, (222, 214, 190, 235), False),
    "costal_cartilages":    ("Kostal kıkırdaklar", KEM, (200, 210, 205, 220), False),
    "hip_left":             ("Sol koksa (pelvis)", KEM, (222, 214, 190, 235), False),
    "hip_right":            ("Sağ koksa (pelvis)", KEM, (222, 214, 190, 235), False),
    "femur_left":           ("Sol femur", KEM, (225, 210, 180, 255), False),
    "femur_right":          ("Sağ femur", KEM, (225, 210, 180, 255), False),
    "humerus_left":         ("Sol humerus", KEM, (222, 214, 190, 235), False),
    "humerus_right":        ("Sağ humerus", KEM, (222, 214, 190, 235), False),
    "scapula_left":         ("Sol skapula", KEM, (222, 214, 190, 235), False),
    "scapula_right":        ("Sağ skapula", KEM, (222, 214, 190, 235), False),
    "clavicula_left":       ("Sol klavikula", KEM, (222, 214, 190, 235), False),
    "clavicula_right":      ("Sağ klavikula", KEM, (222, 214, 190, 235), False),
    "patella":              ("Patella", KEM, (225, 212, 185, 255), False),
    "tibia":                ("Tibia", KEM, (223, 210, 182, 255), False),
    "fibula":               ("Fibula", KEM, (223, 210, 182, 255), False),
    # muscle
    "autochthon_left":      ("Sol paravertebral kas", KAS, (170, 80, 80, 210), False),
    "autochthon_right":     ("Sağ paravertebral kas", KAS, (170, 80, 80, 210), False),
    "iliopsoas_left":       ("Sol iliopsoas", KAS, (180, 85, 85, 210), False),
    "iliopsoas_right":      ("Sağ iliopsoas", KAS, (180, 85, 85, 210), False),
    "gluteus_maximus_left": ("Sol gluteus maksimus", KAS, (175, 82, 82, 210), False),
    "gluteus_maximus_right": ("Sağ gluteus maksimus", KAS, (175, 82, 82, 210), False),
    "gluteus_medius_left":  ("Sol gluteus medius", KAS, (178, 84, 84, 210), False),
    "gluteus_medius_right": ("Sağ gluteus medius", KAS, (178, 84, 84, 210), False),
    "gluteus_minimus_left": ("Sol gluteus minimus", KAS, (182, 86, 86, 210), False),
    "gluteus_minimus_right": ("Sağ gluteus minimus", KAS, (182, 86, 86, 210), False),
    # total_mr görevi bazı yapıları TARAFSIZ/BİRLEŞİK adlarla üretir
    "vertebrae":            ("Vertebralar", KEM, (222, 214, 190, 235), False),
    "ribs":                 ("Kostalar", KEM, (218, 210, 188, 225), False),
    "intervertebral_discs": ("İntervertebral diskler", KEM, (200, 205, 215, 225), False),
    "spinal_canal":         ("Spinal kanal", ORG, (230, 230, 160, 255), False),
}

def classify(name):
    """Return (label, group, rgba, default_on) for any TotalSegmentator name."""
    if name in STRUCTURES:
        return STRUCTURES[name]
    m = re.fullmatch(r"vertebrae_([CTLS]\d+|S1)", name)
    if m:
        return (f"{m.group(1)} vertebra", KEM, (222, 214, 190, 235), False)
    m = re.fullmatch(r"rib_(left|right)_(\d+)", name)
    if m:
        side = "Sol" if m.group(1) == "left" else "Sağ"
        return (f"{side} {m.group(2)}. kosta", KEM, (218, 210, 188, 225), False)
    pretty = name.replace("_", " ").capitalize()
    return (pretty, "Diğer", (160, 160, 170, 220), False)

def detect_volumes(scene_dir):
    vols = []
    for p in sorted((scene_dir / "nifti").glob("*.nii.gz")):
        vols.append({"label": p.name.replace(".nii.gz", ""), "url": f"nifti/{p.name}"})
    return vols

def build(scene_dir, title, volumes=None, volume_opacity=None):
    scene_dir = Path(scene_dir)
    structures_in = json.loads((scene_dir / "structures.json").read_text(encoding="utf-8"))
    out = []
    for s in structures_in:
        label, group, rgba, on = classify(s["name"])
        mesh = s["mesh"]
        # prefer a pre-decimated *_light.stl when present (large joints/bones)
        light = scene_dir / mesh.replace(".stl", "_light.stl")
        if light.exists():
            mesh = mesh.replace(".stl", "_light.stl")
        seg = scene_dir / "segmentations" / f"{s['name']}.nii.gz"
        entry = {
            "name": s["name"], "label": label, "group": group,
            "volume_ml": s["volume_ml"], "mesh": mesh,
            "rgba": list(rgba), "on": on,
        }
        if seg.exists():
            entry["seg"] = f"segmentations/{s['name']}.nii.gz"
        out.append(entry)

    volumes = volumes or detect_volumes(scene_dir)
    if volume_opacity is None:
        # full CT segmentations: start with meshes only; sparse scenes: show the volume
        volume_opacity = 0.0 if len(out) > 5 else 1.0
    scene = {
        "title": title,
        "volumes": volumes,
        "volume_opacity": volume_opacity,
        "structures": out,
    }
    (scene_dir / "scene.json").write_text(json.dumps(scene, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy(TEMPLATE, scene_dir / "viewer.html")
    shutil.copy(TEMPLATE.parent / "niivue.esm.js", scene_dir / "niivue.esm.js")
    print(f"-- scene.json: {len(out)} yapı, {len(volumes)} seri -> {scene_dir/'viewer.html'}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene_dir")
    ap.add_argument("--title", default="Konsil 3D Scene")
    ap.add_argument("--volume", action="append", metavar="LABEL=PATH",
                    help="seri etiketi=nifti yolu (tekrarlanabilir); verilmezse nifti/ taranır")
    ap.add_argument("--volume-opacity", type=float, default=None)
    a = ap.parse_args()
    volumes = None
    if a.volume:
        volumes = []
        for v in a.volume:
            label, sep, url = v.partition("=")
            if not sep:  # '=' yoksa değer yoldur; etiketi dosya adından türet
                url = label
                label = Path(url).name.replace(".nii.gz", "").replace(".nii", "")
            volumes.append({"label": label, "url": url})
    build(a.scene_dir, a.title, volumes, a.volume_opacity)

if __name__ == "__main__":
    main()
