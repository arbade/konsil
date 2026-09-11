---
description: Convene the Konsil medical board on a completed case file (independent specialist round, cross-examination, Reviewer-Gated minutes). Supports --solo for single-model comparison runs
argument-hint: "<case-id> [--solo]"
---

Load and follow the plugin's `board-orchestrator` skill for: **$ARGUMENTS**

Enforce its preconditions strictly (no board without completed intake). Use the plugin's agent definitions (konsil-specialist, konsil-challenger, konsil-checklist, konsil-steward, konsil-reviewer) for all spawns, and the `literature-protocol` and `board-report` skills where the orchestrator says so. Respond to the user in the language of the dialogue/case.
