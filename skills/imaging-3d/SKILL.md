---
name: imaging-3d
description: Deterministic DICOM-to-3D pipeline - convert a CT/MRI disc to per-organ meshes with TotalSegmentator and open a rotatable browser scene (NiiVue) annotated with the radiologist's written findings. No AI interprets any pixel; this is a communication and orientation aid, not diagnosis.
---

# Konsil 3D Imaging Scene

**Hard rule:** no language/vision model interprets image pixels anywhere in this pipeline. Every step is deterministic tooling. The output is a *communication aid* — it helps a patient/family/clinician see where the radiologist's written findings live in 3D. All interpretation stays with the written report.

## Prerequisites (one-time)
Run `scripts/setup_imaging.sh` — checks/installs: `dcm2niix` (brew), Python venv with `TotalSegmentator`, `nibabel`, `scikit-image`, `trimesh`. Model weights (~few GB) download on first run. On Apple Silicon use `--device mps`. Warn the user: full-res segmentation can take 10–45 min on CPU; `--fast` is ~1–3 min and sufficient for a communication scene.

**License note:** TotalSegmentator code and the default `total`/`total_mr` weights are Apache-2.0; several specialized subtasks are **non-commercial only**. This skill uses only the default task. Audit before any commercial redistribution.

## Pipeline
```
cases/<case-id>/inbox/DICOM/ 
  → scripts/dicom_to_scene.py --fast --device mps
      1. dcm2niix  → NIfTI volume
      2. TotalSegmentator (default task) → per-structure NIfTI masks
      3. marching cubes (scikit-image) → decimated STL per structure (trimesh)
      4. structure volumes (ml) → structures.json  (this structured data MAY be given to the board as text)
      5. scripts/build_scene_viewer.py → scene.json (Turkish labels/groups/colors per structure)
         + copies the SHARED viewer template skills/imaging-3d/assets/viewer.html
         + copies the vendored NiiVue bundle (assets/niivue.esm.js) next to it (offline, pinned version)
  → cases/<case-id>/scene/   (serve the dir: python3 -m http.server -d scene/, open viewer.html)
```

## Viewer (one template for every case)
All cases use the same data-driven viewer (`assets/viewer.html`); per-case content lives only in `scene.json`:

```json
{
  "title": "Konsil — Abdomen BT (23.05.2026)",
  "volumes": [{"label": "Seri 4 — Sagittal T1", "url": "nifti/Seri4.nii.gz"}],
  "volume_opacity": 0.0,
  "structures": [{"name": "liver", "label": "Karaciğer", "group": "Organlar",
                  "volume_ml": 1982.4, "mesh": "meshes/liver.stl", "rgba": [150,90,60,220],
                  "on": true, "seg": "segmentations/liver.nii.gz"}]
}
```
(`seg` is present only when the mask file exists; `on` marks default-visible structures; `volume_opacity` defaults to 0 for scenes with >5 structures, else 1.) Never hand-edit a case's viewer.html — fix the template and re-run `build_scene_viewer.py <scene_dir> --title "..."` (idempotent; safe on existing scenes). Features: 3D render / MPR modes, series dropdown (multi-sequence MR), grouped structure list with per-organ show/hide, solo (◐), and slice-focus (⌖ = jump MPR crosshair to the organ centroid and overlay its segmentation mask). NiiVue version is pinned in the template; UI handlers bind before any network load so controls never go dead if a mesh fails.

## Annotation step (text-only)
After the scene is built, read the case file's imaging-report findings and write `scene/annotations.json`: quoted report text + the *named structure* it belongs to. Placement is by structure name from the segmentation output — never by looking at the images. If a finding's structure isn't in the segmentation set, list it under `not_localizable`. If the quoted report is from a DIFFERENT study than the scene's source volume, say so in `source` and in the top-level `note`. Schema:

```json
{
  "note": "provenance + 'yorum radyoloğa aittir' disclaimer",
  "annotations": [{"structure": "kidney_right", "source": "US raporu 10.09.2026", "text": "verbatim quote",
                   "marker": {"region": "mid", "label": "40×31 mm miks lezyon — rapor: orta kortikal alan"}}],
  "not_localizable": [{"source": "...", "text": "..."}]
}
```

`marker` is optional and maps the report's own REGION wording to structure geometry: `region` is one of `upper|mid|lower|center` ("üst pol"→`upper`, "orta ..."→`mid`, "alt pol"→`lower`), chosen from the report TEXT only. The viewer anchors it at the centroid of that superior–inferior third of the structure's own mesh — pure geometry on the deterministic segmentation, never pixel interpretation — draws a 3D label there (prefixed "≈") and jumps the ⌖ crosshair to it. A marker is NOT the lesion's exact position; the `note` must say so. If the report gives no location wording, omit `marker`.

The viewer picks this file up automatically (optional — absent file changes nothing): structures with annotations get a 📄 badge, the quotes appear in the sidebar panel when the badge is clicked or the structure is slice-focused (⌖), and `not_localizable` items are listed at the bottom of the sidebar.

## What the board may consume
Only `structures.json` (names + volumes) and the written reports. Never screenshots of the scene.
