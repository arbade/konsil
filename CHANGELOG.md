# Changelog

All notable changes to Konsil are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-24

This release rebuilds the imaging experience around a single shared 3D viewer,
brings the written radiology report directly into the scene, and introduces an
explicitly consent-gated, OFF-PROTOCOL AI image read — while keeping the
default no-AI-on-pixels rule fully intact.

### Added

- **Shared data-driven 3D viewer** — one viewer template
  (`skills/imaging-3d/assets/viewer.html`) driven by a per-case `scene.json`.
  NiiVue 0.69.0 is vendored so every generated scene works fully offline with a
  pinned version. `build_scene_viewer.py` maps all TotalSegmentator structures
  to labels, groups, and colors, prefers lightweight meshes, and detects series.
- **Per-organ controls** — show/hide with lazy mesh loading, solo mode (◐), and
  MPR slice-focus (⌖) that jumps the crosshair to the organ centroid with its
  segmentation mask overlaid.
- **Report annotations in the viewer** — quoted findings from the written
  radiology report, mapped by structure name via `annotations.json`, rendered
  as 📄 badges with a sidebar quote panel, a provenance note, and an explicit
  "not localizable in scene" list.
- **Report region markers** — the report's own location words (e.g. "upper
  third") are mapped to a structure's upper/mid/lower third by pure geometry on
  the deterministic segmentation mask — never by pixel interpretation. The
  viewer draws an approximate ("~") 3D label with a leader line, jumps the
  crosshair there, and states in the status line that the mark is approximate.
- **Consistent zoom** — a zoom slider that behaves identically across the 3D
  render and MPR views, stays in sync with wheel zoom, and is restored by
  Reset together with pan.
- **OFF-PROTOCOL AI image read (`/konsil:okuma`)** — a new, strictly opt-in
  path: DICOM is rendered deterministically (`scripts/dicom_to_png.py`) and a
  dedicated image-reader agent produces a blind, confidence-graded
  observational read. Every output carries an immutable "AI result — not an
  official report" disclaimer block. The read requires explicit logged consent,
  is quarantined from board evidence, and never substitutes the formal
  radiology report. The Reviewer Gate gains a fifth checklist (off-protocol
  read compliance).
- **Discovery docs** — design records for why the AI must not measure lesions
  from pixels (CADe/CADx SaMD, MDR Rule 11) and for the off-protocol read's
  consent and quarantine design.
- **README gallery** — abdomen CT rows and refreshed knee MR captures, all
  from patient-consented, identity-free imagery.

### Changed

- **Board minutes disclaimer** is now conditional: it correctly accounts for
  cases that contain a consented off-protocol AI read and for cases where no
  written radiology report exists, instead of asserting an unconditional
  "no images were interpreted by AI" statement.
- README installation instructions point to the real GitHub source.

### Fixed

- 39 audited viewer and pipeline defects, including: focus race conditions
  (generation counter — no more orphan mask overlays), late mesh/mask loads
  adopted or discarded instead of becoming uncontrollable, retryable mesh load
  errors, Reset restoring scene opacity and clip in any mode, XSS-safe DOM
  building, scene/volume load failures surfaced without killing init, and
  narrow-window layout no longer clipping the footer.
- 17 confirmed findings from an adversarial verification pass on the marker
  and zoom features, including silent glyph loss in 3D labels ("94 cm³" →
  "94 cm"), leader lines pointing at the canvas corner, and same-region
  markers being merged instead of given a fabricated anatomical offset.
- Dead viewer controls (handlers now bind before any network load) and
  invisible meshes (extension handling and delayed redraw after async mesh
  buffer updates).
- Pipeline robustness: trimesh ≥ 4 decimation signature, stale dcm2niix
  output cleanup, all converted series exposed in the series menu, UTF-8 I/O,
  and `--volume` parsing without `=`.

## [0.1.0] - 2026-09-11

Initial release of Konsil — an adversarial AI medical case-review board for
Claude Code.

### Added

- **Case intake (`/konsil:case`)** — builds a structured, verified case file
  from a folder of mixed patient documents, with a Missing Data Gate before
  any board may convene.
- **Board (`/konsil:board`)** — blind, independent specialist first
  assessments in isolated contexts, followed by an adversarial
  cross-examination round; supports `--solo` comparison runs.
- **Fixed board officers** — Challenger (devil's advocate), Checklist
  (can't-miss auditor), and Steward (cost and sequencing).
- **In-session citation verification** for literature claims.
- **Reviewer-Gated, dissent-preserving board minutes** audited by parallel
  reviewers (citation integrity, dissent integrity, safety language,
  completeness).
- **Longitudinal follow-up (`/konsil:update`)** — folds new results into an
  existing case and re-convenes the board in delta mode.
- **Deterministic DICOM-to-3D pipeline (`/konsil:imaging`)** — TotalSegmentator
  meshes in a rotatable browser scene as a communication aid; no AI interprets
  any pixel.
