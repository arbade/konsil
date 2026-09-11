---
description: Intake a case - build a structured, verified case file from a folder of patient documents and run the Missing Data Gate
argument-hint: "<case-id or path to document folder>"
---

Load and follow the plugin's `case-intake` skill for the case the user specified: **$ARGUMENTS**

If the argument is a path to loose documents, create `cases/<case-id>/inbox/`, move/copy the documents there (ask for a case id if none given), then run intake. If it is an existing case id, resume its intake. Do not convene any board from this command; end by reporting intake status and, if pending, the targeted anamnesis questions.
