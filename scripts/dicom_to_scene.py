#!/usr/bin/env python3
"""Konsil deterministic DICOM -> 3D scene pipeline.

DICOM dir -> dcm2niix -> NIfTI -> TotalSegmentator -> per-structure STL meshes
-> structures.json (name + volume ml) -> viewer.html (NiiVue, rotatable in browser).

No AI touches pixels anywhere in this file. Communication aid, not diagnosis.

Usage:
  python dicom_to_scene.py <dicom_dir> <out_dir> [--fast] [--device mps|cpu|gpu] [--mr]
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

# baştan import et: saatlik segmentasyon bittikten sonra ImportError ile iş kaybetme
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_scene_viewer import build as build_viewer

def run(cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run([str(c) for c in cmd], check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dicom_dir"); ap.add_argument("out_dir")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--mr", action="store_true", help="use total_mr task for MRI")
    ap.add_argument("--title", default="Konsil 3D Scene", help="viewer title, e.g. 'Konsil — Abdomen BT (23.05.2026)'")
    a = ap.parse_args()

    out = Path(a.out_dir); out.mkdir(parents=True, exist_ok=True)
    nifti_dir = out / "nifti"; nifti_dir.mkdir(exist_ok=True)
    seg_dir = out / "segmentations"
    mesh_dir = out / "meshes"; mesh_dir.mkdir(exist_ok=True)

    # 1. DICOM -> NIfTI (önce eski çalıştırmanın volume* kalıntılarını temizle —
    # dcm2niix üstüne yazmaz, bayat seriler yanlışlıkla seçilebilir)
    for stale in nifti_dir.glob("volume*"):
        stale.unlink()
    run(["dcm2niix", "-z", "y", "-f", "volume", "-o", nifti_dir, a.dicom_dir])
    vols = sorted(nifti_dir.glob("volume*.nii.gz"))
    if not vols:
        sys.exit("dcm2niix produced no NIfTI volume")
    vol = vols[0]
    if len(vols) > 1:
        print(f"! {len(vols)} series converted; using {vol.name}. Re-run pointing dcm2niix at one series for others.")

    # 2. Segmentation (default Apache-2.0 task only)
    cmd = ["TotalSegmentator", "-i", vol, "-o", seg_dir, "--device", a.device]
    if a.fast: cmd.append("--fast")
    if a.mr: cmd += ["--task", "total_mr"]
    run(cmd)

    # 3. Masks -> STL meshes + volumes
    import nibabel as nib
    import numpy as np
    from skimage import measure
    import trimesh

    structures = []
    for mask_path in sorted(Path(seg_dir).glob("*.nii.gz")):
        img = nib.load(str(mask_path))
        data = np.asarray(img.dataobj)
        if data.max() == 0:
            continue
        name = mask_path.name.replace(".nii.gz", "")
        voxel_ml = float(np.prod(img.header.get_zooms()[:3])) / 1000.0
        vol_ml = round(float((data > 0).sum()) * voxel_ml, 1)
        try:
            verts, faces, _, _ = measure.marching_cubes(data.astype(np.uint8), level=0.5)
            verts = nib.affines.apply_affine(img.affine, verts)  # to scanner mm space
            mesh = trimesh.Trimesh(vertices=verts, faces=faces)
            try:
                mesh = mesh.simplify_quadric_decimation(percent=0.25)  # trimesh >= 4
            except TypeError:
                mesh = mesh.simplify_quadric_decimation(int(len(mesh.faces) * 0.25) or 1000)  # eski imza: face_count
            mesh.export(str(mesh_dir / f"{name}.stl"))
            structures.append({"name": name, "volume_ml": vol_ml, "mesh": f"meshes/{name}.stl"})
        except Exception as e:
            print(f"! mesh failed for {name}: {e}")

    (out / "structures.json").write_text(json.dumps(structures, indent=2))
    print(f"-- {len(structures)} structures -> structures.json")

    # 4. Viewer — shared template + scene.json (see build_scene_viewer.py)
    # dcm2niix birden çok seri üretmişse hepsi seri menüsüne girsin (segmentasyon yine vols[0] üzerinden)
    build_viewer(out, title=a.title,
                 volumes=[{"label": v.name.replace(".nii.gz", ""), "url": f"nifti/{v.name}"} for v in vols])
    print(f"-- open {out/'viewer.html'} in a browser (serve dir: python3 -m http.server -d {out})")

if __name__ == "__main__":
    main()
