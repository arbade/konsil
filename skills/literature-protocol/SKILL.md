---
name: literature-protocol
description: Shared evidence rules and API cookbook for all Konsil board members - how to search Europe PMC/PubMed/guideline bodies and how to verify every citation before it may appear in any output. Load when performing or auditing the literature step.
---

# Konsil Literature Protocol

The board's credibility rests on one rule: **a citation that was not retrieved and verified in this session does not exist.** LLM-fabricated references measured at 18–29% in unguarded systems are the primary failure mode this protocol eliminates.

## Source hierarchy (search in this order)

1. **Clinical practice guidelines** (EAU, AUA, NICE, ESC, ADA, USPSTF, specialty societies) — WebFetch the guideline page directly.
2. **Systematic reviews / meta-analyses** — Europe PMC with `AND (SRC:MED) AND (PUB_TYPE:"Review" OR "systematic review" OR "meta-analysis")`.
3. **Primary studies** — only when 1–2 are silent; prefer recent, larger, prospective.
4. General web (WebSearch/WebFetch) — for guideline discovery and society positions only, never as the final citation for a clinical figure if a primary source is findable.

## API cookbook (all free; no keys required except where noted)

**Europe PMC (primary workhorse — 10 req/s, no key):**
```bash
# Search (title/abstract), newest first, JSON:
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=%22complex%20renal%20cyst%22%20AND%20bosniak&format=json&pageSize=10&sort=P_PDATE_D%20desc"
# Fetch one record's metadata by PMID:
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:35999371%20AND%20SRC:MED&format=json"
# Open-access full text (XML) when isOpenAccess=Y:
curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9623069/fullTextXML"
```

**PubMed E-utilities (secondary — 3 req/s keyless):**
```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=bosniak+classification+meta-analysis&retmode=json&sort=pub_date"
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=35999371&retmode=json"
```

**LOINC mapping for lab tests (NLM Clinical Tables — free, no key):**
```bash
curl -s "https://clinicaltables.nlm.nih.gov/api/loinc_items/v3/search?terms=creatinine+serum"
```

**Do NOT use:** Semantic Scholar (restrictive license), WikEM (ToS prohibits AI use), UpToDate/OpenEvidence (closed). OpenAlex requires an API key since Feb 2026 — optional, not default.

## Mandatory verification procedure (before ANY citation enters output)

1. Retrieve the record (one of the calls above, or WebFetch the URL).
2. Confirm the **title** and **year** match what you are attributing to it.
3. For load-bearing figures (a percentage, threshold, or recommendation grade): confirm the figure appears in the abstract/full text you retrieved — not just in your memory of the paper.
4. Cite as: `[First-author Year, Journal — PMID or URL]`.
5. Log the search string that found it in your Search log section.

**Failure handling:** can't verify → the claim is stated as reasoning and marked `[UNSOURCED]`; numeric guesses marked `[ESTIMATE]`. These markers are protected: the Reviewer Gate fails any draft that silently drops them.
