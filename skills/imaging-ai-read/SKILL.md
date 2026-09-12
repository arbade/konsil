---
name: imaging-ai-read
description: OFF-PROTOCOL AI image read - render a DICOM deterministically (scripts/dicom_to_png.py) and have a dedicated reader agent produce a systematic, confidence-graded observational read - runs ONLY on the user's explicit typed consent, is always labeled OFF-PROTOCOL, and never substitutes or waives the formal radiology report; the default no-AI-on-pixels rule of every other pipeline is untouched.
---

# Konsil Off-Protocol AI Image Read

Input: a case-id (images under `cases/<id>/inbox/`) OR a direct path to an image/DICOM file. Output: `cases/<case-id>/ai-reads/read-<YYYY-MM-DD>-<slug>-OFF-PROTOCOL.md`, an "AI Görüntü Okumaları (OFF-PROTOCOL)" section in `case.md`, and a consent record in `ai-reads/memlog.md`. This skill is physically separate from `imaging-3d` — the skill that carries the hard rule never carries its exception.

**Case binding rule (blocking):** every consent record and every output path below is case-bound, so a read cannot run without a case id. If the input is a direct image/DICOM path, resolve the case id BEFORE Step 0: ask the user which existing case the image belongs to; if it belongs to no existing case, create one first (run `case-intake` on the image's folder, or — if the user declines full intake — create a minimal `cases/<id>/` workspace with a stub `case.md` whose `intake_status` stays `pending`, and copy the image into `cases/<id>/inbox/`). Never log consent or write a read anywhere outside `cases/<id>/ai-reads/`. A stub case created this way still cannot convene a board (intake stays pending).

**Hard rule (unchanged default):** the no-AI-on-pixels rule in `imaging-3d` stays in full force everywhere else. This skill is not an exception to that rule — it is a separate, user-consented mode that never runs implicitly.

**Consent rule (blocking):** no read without the user's exact typed sentence (Step 0). A conversational "evet/olur" is NOT consent.

**Report rule:** the output never closes the Missing Data Gate's missing-radiology-report flag and never counts as an imaging report in case intake.

**Naming rule:** every output file name ends in `-OFF-PROTOCOL.md` — no exceptions.

## Step 0 — Consent Gate (blocking)
1. **State the risks to the user, in Turkish, before anything else** — an AI read can miss findings and can invent findings that are not there; it never replaces the formal radiology report; warn explicitly against automation bias ("makine gördü, tamamdır" tuzağı — okuma ne kadar akıcı görünürse görünsün doğrulanmamıştır).
2. **Ask the user to type the exact sentence:** `OFF-PROTOCOL OKUMAYI ONAYLIYORUM` — no other phrasing, paraphrase, or affirmation is accepted, because consent to leave a safety default must be unambiguous and auditable.
3. **Record the consent APPEND-ONLY** in `cases/<id>/ai-reads/memlog.md`: timestamp, the user's verbatim sentence, and the target image path. If a board run is active, also append a single reference line to that board's memlog. Never edit or overwrite earlier memlog lines — corrections are new lines.

If the exact sentence is not given: **Refuse to proceed.**

## Step 1 — Deterministic render
- If the input is DICOM, render with the venv python (the venv location honors the same `KONSIL_VENV` override as `scripts/setup_imaging.sh`): `"${KONSIL_VENV:-$HOME/.konsil-venv}/bin/python" scripts/dicom_to_png.py <in.dcm> cases/<id>/ai-reads/renders/<name>.png`. The render is deterministic tooling — all INTERPRETATION lives only in the reader agent, never in this step.
- If the input is already PNG/JPEG, copy it into `ai-reads/renders/` and note in the provenance record: "harici render, pencere bilinmiyor" — an externally windowed image may hide or exaggerate findings, and the reader must know that.
- Append the render command and the script's output line to `ai-reads/memlog.md`.

## Step 2 — Spawn the reader
Spawn ONE `konsil-image-reader` agent. Give it in the spawn prompt: the rendered PNG path, the `case.md` path, **the path to the logged consent record (`cases/<id>/ai-reads/memlog.md`, written in Step 0 — the agent's rule 1 REFUSES to read without it)**, the case-file language, the study date/modality (taken from the DICOM header), and the instruction that its own agent-spec protocol rules apply in full. Same evidence rules as every member (verified citations; `[UNSOURCED]`/`[ESTIMATE]` markings; no fabrication — summary; full version in the literature-protocol skill).

**Do NOT give the agent the formal radiology report even if one exists** — the read is blind, so it cannot anchor on the radiologist's wording. Comparison mode (a difference table against the formal report) is deliberately deferred to v2 (discovery F8).

## Step 3 — Output placement
Save the agent's output as `cases/<id>/ai-reads/read-<YYYY-MM-DD>-<study-slug>-OFF-PROTOCOL.md`. The TOP header block and the BOTTOM disclaimer block are MANDATORY and must match the templates byte-for-byte (Reviewer Gate E audits them — see `agents/reviewer.md`).

Top block (first lines of the file):

```
**OFF-PROTOCOL — yapay zekâ görsel okuması; resmi radyoloji raporu yerine geçmez.** Kullanıcının açık, kayıtlı onayıyla (bkz. ai-reads/memlog.md) piksel-yorum yasağının dışında üretilmiştir. Klinik korelasyon ve resmi radyolog raporu zorunludur.
```

Bottom block (last lines of the file, do not modify):

```
---

> **OFF-PROTOCOL — ZORUNLU UYARI (bu blok değiştirilemez ve kısaltılamaz):**
> Bu bir yapay zekâ sonucudur; resmi radyoloji raporu değildir ve yerine geçmez; klinik korelasyon şarttır.
> Bu okuma kullanıcının açık ve kayıtlı talebiyle, varsayılan piksel-yorum yasağının dışında (OFF-PROTOCOL) üretilmiştir.
> Resmi radyolog raporu gereksinimi geçerliliğini korur: bu belge o gereksinimi ve Missing Data Gate'teki "resmi radyoloji raporu eksik" bayrağını KAPATMAZ. Görüntüler bir radyolog tarafından resmî olarak raporlanmalıdır.
```

**Self-check (mandatory, every run):** Reviewer Gate E only audits reads that reach a board — a standalone `/konsil:okuma` run must verify itself. After saving, mechanically diff (e.g., `diff <(head ...) <(...)` or byte comparison via Bash) the saved file's top header block and bottom disclaimer block against the two templates above, and confirm the file name ends in `-OFF-PROTOCOL.md`. Any mismatch: fix the file and re-check before Step 4; log the self-check result as a line in `ai-reads/memlog.md`.

## Step 4 — Case file integration (two-track)
Two-track integration (discovery F7): add or update a `## AI Görüntü Okumaları (OFF-PROTOCOL)` section in `case.md` with the table:

```
| Tarih | Çalışma | Okuma dosyası | Vaka dosyasına işlenen teknik olgular |
```

- **Technical facts only** (burned-in side marker, projection, exposure/quality) may fill gaps in the case file's other sections — they are properties of the image object, not interpretations of anatomy — and each one carries the provenance tag `[KAYNAK: OFF-PROTOCOL AI okuması <tarih>]`.
- **Interpretive findings** (no fracture, no lesion, ...) are quarantined: they live only in the read file and behind this section's link, and NEVER enter the Problem List or Imaging Findings — an unverified AI impression must not masquerade as case evidence.
- `intake_status` and the missing-formal-report flag DO NOT CHANGE.

## What the board may consume
The board may consume this read only in a separate, OFF-PROTOCOL-labeled section that cites the read file by name — never blended into regular imaging evidence. If it enters the minutes, the Reviewer Gate gains a fifth auditor (E) — see the board-report skill.
