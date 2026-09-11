---
name: case-update
description: Longitudinal follow-up - fold new results into an existing Konsil case file, compute what changed (trends, growth rates, resolved/new problems), and re-convene the board in delta mode so the new minutes lead with what changed since last time.
---

# Konsil Case Update (Longitudinal Mode)

The board's memory is the case folder. When new documents arrive for an existing case:

## Step 1 — Delta intake
Run `case-intake` steps 1–3 on the new documents only, then merge into `case.md`:
- New rows in the timeline table (never overwrite old rows — corrections are new rows flagged `[CORRECTS <date>]`).
- **Computed deltas:** for every measurement that now has ≥2 dated values, compute the change and rate (e.g., mm/year, eGFR slope). These go in a `## Interval Changes` section — this is the single highest-value output of longitudinal mode.
- New inconsistency flags, including cross-time ones (a finding described in an old report that the new report silently drops = **orphaned finding**, flagged).

## Step 2 — Delta gate
Ask only the questions the new data raises (new symptoms since last board? treatments started?). Update `intake_status`.

## Step 3 — Re-convene in delta mode
Run `board-orchestrator` with the delta framing: prior minutes are provided to Round-1 specialists **as history** (this is a follow-up, not a fresh case — the prior board's positions are data, marked as such), and the Round-1 task adds: "state explicitly which prior recommendations were followed, which are pending, and whether the interval changes alter the prior assessment."

## Step 4 — Delta minutes
Same template; the Executive section leads with **What changed / What it means / What was recommended last time vs what happened**. Time-sensitive escalations (e.g., a growth rate crossing a guideline threshold) are the headline, cited.
