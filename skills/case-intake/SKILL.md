---
name: case-intake
description: Build a structured case file from a folder of mixed patient documents (report PDFs, lab printouts/photos, discharge summaries, DICOM discs) - timeline, problem list, labs with reference-range plausibility checks, inconsistency flags - then run the Missing Data Gate before any board may convene.
---

# Konsil Case Intake

Input: a case directory (e.g. `cases/<case-id>/inbox/`) containing whatever the user has — PDFs, photos of lab printouts, prior reports, pathology, a DICOM disc copy. Output: a structured case file the board can trust, or a refusal to proceed with targeted questions.

**Language rule:** the case file and all questions to the user are written in the language of the source documents / user dialogue.

## Step 1 — Inventory
List every file. Classify: lab report / imaging report / pathology / clinical note / imaging pixels (DICOM/JPEG of scans) / other. **Pixels are never interpreted here** — note their existence for the `imaging-3d` skill and move on. Record document dates; unreadable or undated files go on the missing-data list.

## Step 2 — Extraction with verification
- **Labs:** extract analyte, value, unit, and the reference range *printed on that report* (ranges are lab-specific — never substitute remembered ranges). Map analytes to LOINC via the NLM Clinical Tables API (see `literature-protocol`). Plausibility check every value against its printed range and physiologic possibility; photo-extracted values are lower-trust — re-read the image a second time independently and reconcile; any mismatch or implausible value goes to the user for confirmation before it enters the case file.
- **Imaging reports:** extract findings verbatim-faithful (measurements with dates), impression, and recommendations. Do not editorialize.
- **Cross-document checks:** recompute what can be recomputed (e.g., volumes from stated dimensions; growth rates between dated measurements; age vs dates). Every discrepancy becomes an **Inconsistency Flag** — these are product, not noise; boards have caught real report errors this way.

## Step 3 — Assemble `case.md` (template: `templates/case-file.md`)
Demographics as documented · problem list · **timeline table** (every dated event/measurement, one row each, so trends are computable) · labs table · imaging findings by date · procedures & pathology · medications/history *as documented* · Inconsistency Flags · source map (every fact → source file).

## Step 4 — Missing Data Gate (blocking)
Evidence shows model accuracy collapses on thin, self-reported histories. Therefore:
1. Generate the gaps list: undocumented symptoms/duration, medications, relevant history (family, smoking, occupational), prior reports referenced but absent, key labs never obtained.
2. Ask the user the **targeted anamnesis questions** (grouped, concrete, answerable — not a form dump; ≤10 at once).
3. Only after answers — or the user's explicit "proceed with gaps" — set `intake_status: complete` (or `complete-with-gaps`, listing them) in `case.md` frontmatter.

**The board orchestrator must refuse to convene while `intake_status` is absent or `pending`.**
