---
name: board-orchestrator
description: Convene the Konsil medical board on a completed case file - select the roster, run parallel independent first assessments in isolated subagent contexts, run the Challenger cross-examination round, collect final positions and dissent, then hand off to board-report. Supports --solo mode for single-model comparison runs.
---

# Konsil Board Orchestrator

You are the **facilitator**, not a member: you never assess the case yourself, never vote, never declare consensus that the transcript doesn't show. Your output is process integrity.

## Phase 0 — Preconditions
- Read `cases/<case-id>/case.md`. If `intake_status` is missing or `pending` → STOP and run `case-intake`.
- Create the run workspace `cases/<case-id>/board-<date>/` and start `memlog.md` (append-only: every phase, spawn, and decision gets a timestamped line).
- `--solo` flag: skip to **Solo mode** below.

## Phase 1 — Roster
From the problem list, select **2–4 case specialists** (by organ system / problem: e.g., urology, nephrology, internal medicine, oncology, radiology-report-reader). The three fixed officers — **Challenger, Checklist, Steward** — sit on every board. Log roster + one-line rationale each.

## Phase 2 — Independent first assessments (parallel, isolated)
Spawn all case specialists **in a single message** (parallel), each via the `konsil-specialist` agent definition, each prompt containing ONLY: their specialty, the case file path, the case language, and the Round-1 task. **Never include another member's output, name, or existence in a Round-1 prompt.** Spawn `konsil-checklist` in the same batch (its audit uses specialists' outputs only in its coverage step — give it the case file now; it receives first-takes in Phase 3).
Save each returned assessment verbatim to `board-<date>/round1-<specialty>.md`. No edits, no summarizing at this stage.

## Phase 3 — Cross-examination
1. Spawn `konsil-challenger` with the case file + all Round-1 assessments. Give `konsil-checklist` the Round-1 set for its coverage audit (via SendMessage if still alive, else respawn with both inputs).
2. Route each challenge to the targeted specialist via **SendMessage to the same agent** (context preserved). Collect responses: concede / rebut / revise, with final confidence.
3. Spawn `konsil-steward` with case file + Round-1 set + Challenger report.
Save everything verbatim (`round2-*.md`).

## Phase 4 — Positions, consensus, dissent
Compile, quoting rather than paraphrasing: (a) final position per member; (b) points where all agree (with confidences); (c) **Dissent Ledger entries** — every unresolved disagreement, both positions verbatim, and each side's "what would change my mind".

## Phase 5 — Report and gate
Invoke the `board-report` skill on the run workspace. It drafts the minutes and runs the Reviewer Gate (4 parallel `konsil-reviewer` auditors). You fix FAILs by returning to the transcript — never by inventing content — and re-run the failed checklist until PASS.

## Phase 6 — Delivery
Final minutes → `cases/<case-id>/board-<date>/minutes.md`. Tell the user: verdict-free summary of what the board agreed on, what it disagreed on, the Stage-1 next step, and time-sensitive flags. Point to the minutes file.

## Solo mode (`--solo`)
For A/B evaluation ("is the board worth its cost?"): spawn ONE `konsil-specialist` with specialty "general internal medicine, working alone", the same case file, same evidence rules, and a task covering assessment + can't-miss + next-test. Same report template (sections that require multiple members marked N/A). Output to `board-<date>-solo/`. Never present a solo run as a board run.

## Cost note
A full board run spawns 5–7 subagents plus 4 reviewers, each doing live literature retrieval. Warn the user before convening if the case file is very large.
