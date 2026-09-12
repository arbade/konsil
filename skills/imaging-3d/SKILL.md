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
  → cases/<case-id>/scene/   (serve the dir: python3 -m http.server -d scene/, open viewer.html)
```

## Viewer (one template for every case)
All cases use the same data-driven viewer (`assets/viewer.html`); per-case content lives only in `scene.json`. Never hand-edit a case's viewer.html — fix the template and re-run `build_scene_viewer.py <scene_dir> --title "..."` (idempotent; safe on existing scenes). Features: 3D render / MPR modes, series dropdown (multi-sequence MR), grouped structure list with per-organ show/hide, solo (◐), and slice-focus (⌖ = jump MPR crosshair to the organ centroid and overlay its segmentation mask). NiiVue version is pinned in the template; UI handlers bind before any network load so controls never go dead if a mesh fails.

## Annotation step (text-only)
After the scene is built, read the case file's imaging-report findings and add each written finding to `annotations.json` as: quoted report text + the *named structure* it belongs to (e.g., "right kidney, mid-pole — per report: 40×31 mm mixed lesion"). Placement is by structure name from the segmentation output — never by looking at the images. If a finding's structure isn't in the segmentation set, list it under "not localizable in scene".

## What the board may consume
Only `structures.json` (names + volumes) and the written reports. Never screenshots of the scene.
