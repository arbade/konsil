---
name: board-report
description: Draft the Konsil board minutes from a completed board run's transcripts using the minutes template, then run the Reviewer Gate (four parallel auditors - citation integrity, dissent integrity, safety language, completeness) until all pass - plus a fifth off-protocol compliance auditor when the case contains an AI image read.
---

# Konsil Board Report

Input: a board run workspace (`cases/<case-id>/board-<date>/`) with Round-1/Round-2 transcripts and the orchestrator's Phase-4 compilation. Output: `minutes.md` that has passed all assigned Reviewer Gate checklists (four, plus E when an AI image read is in play).

## Drafting rules

1. Use `templates/board-minutes.md` verbatim as the skeleton. Every section filled or explicitly `N/A — <reason>`.
2. **Quote, don't launder.** Positions, dissents, and confidences come from the transcripts, quoted or tightly faithful. The minutes may organize; they may not smooth. If the transcript shows disagreement, the minutes show disagreement.
3. **No singular verdict.** The minutes never say "the diagnosis is X." They say what the board converged on, at what confidence, and what remains open.
4. Every recommendation carries: proposing member(s), rationale, citations (already verified upstream), urgency class.
5. Preserve every `[UNSOURCED]` / `[ESTIMATE]` marker.
6. The disclaimer block from the template is untouchable — same wording, top position.
7. Write in the case language. Plain language where possible; technical terms kept but explained once.
8. **OFF-PROTOCOL reads are quarantined in the minutes.** If the case has any `ai-reads/*-OFF-PROTOCOL.md`, quote it only inside a dedicated, clearly labeled "OFF-PROTOCOL AI Görüntü Okuması" subsection that names the source file, keeps the read's own disclaimer visible, and states that the formal radiology report requirement remains open. The read never feeds the consensus/differential sections directly; only its provenance-tagged technical facts may be referenced elsewhere.

## Reviewer Gate

Spawn **four `konsil-reviewer` agents in one message** (five when the case workspace contains any `ai-reads/*-OFF-PROTOCOL.md` **OR the minutes, transcripts, or case file reference an AI image read in any way** — same trigger as `agents/reviewer.md` E; a read that violated the naming or placement rules must still summon its auditor) (parallel), one per checklist:
- A — Citation integrity (re-resolves every citation)
- B — Dissent integrity (transcript vs ledger)
- C — Safety language
- D — Completeness & traceability
- E — Off-protocol read compliance (only when an AI image read exists)

Any FAIL: fix the draft **from the transcripts only** (if information is genuinely absent, the fix is to say it's absent), append the fix to `memlog.md`, and re-run the failed checklist with a fresh reviewer. Repeat until every assigned checklist PASSes (4×, or 5× when E is assigned). Record the final gate result in the minutes' appendix.
