---
description: OFF-PROTOCOL AI image read - deterministic render then a consent-gated, confidence-graded observational read. Never a substitute for the formal radiology report; the default no-pixels rule stays intact
argument-hint: "<case-id | path-to-dicom-or-image>"
---

Load and follow the plugin's `imaging-ai-read` skill for: **$ARGUMENTS**

Enforce the Consent Gate strictly — no read of any kind before the user types the exact consent sentence and it is logged; a conversational yes is not consent.

This command never weakens the default rule: do not run it implicitly from any other command or skill, and never present its output as a radiology report. Respond to the user in the language of the dialogue/case.
