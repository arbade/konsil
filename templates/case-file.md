---
case_id: {case-id}
created: {date}
language: {case language}
intake_status: pending   # pending | complete | complete-with-gaps
gaps_accepted: []        # filled when user says "proceed with gaps"
---

# Case File — {case-id}

## Demographics (as documented)
*(Age/DOB, sex, only what the documents state — no inference.)*

## Problem List (ranked)

## Timeline
| Date | Event / Measurement | Value & unit | Source file |
|---|---|---|---|
*(One row per dated fact. Corrections are new rows flagged `[CORRECTS <date>]` — never overwrite.)*

## Interval Changes
*(Computed deltas for every measurement with ≥2 dated values: absolute change, rate per year. Populated by case-update.)*

## Laboratory Results
| Date | Analyte (LOINC) | Value | Unit | Printed ref. range | Flag | Source |
|---|---|---|---|---|---|---|
*(Ranges come from the report itself. Photo-extracted values double-read; user-confirmed if mismatched.)*

## Imaging Findings (from written reports only)
*(Per study: date, modality, institution, findings faithful to the report, impression, recommendations. No pixel interpretation.)*

## Procedures & Pathology

## Medications & History (as documented / as answered at intake)

## Inconsistency Flags
*(Recomputation mismatches, impossible values, cross-document contradictions, orphaned findings.)*

## Source Map
*(Every fact class → source file, so the board can trace any datum to its document.)*
