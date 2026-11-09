# SupportPick: safe operating, verified-benefit editorial, and monetization review

Draft-only, no live service mutation, API collection, publishing, advertisement requests, secret changes, or R2 work.

## 1. Reliability and free backup

- Existing full-data collection, two-generation validation and fail-closed restoration remain unchanged. The source repository's `data.json` can be a **one-item bootstrap sample**, not the current production snapshot. Never replace the validated 10,942-item generation with this sample.
- Existing Google Drive independent backup copies are retained; creation of a daily automatic backup was scheduled separately. This PR does not duplicate its schedule or Google credentials.
- Keep Threads posting ledger, one-reservation-per-slot, immutable main receipt, and no-replay-on-ambiguous-send rules.
- Monitor free Actions artifact storage; no additional recurring workflows or bulk exports here.

## 2. Search relevance and editorial freshness

- `tools/editorial_freshness_audit.py` inspects the existing `guides.json` and `editorials.json` (not the sample production data) to flag expired or soon-expiring source reviews, missing validity, unverified publication URLs and missing benefit identity.
- Review-only report contains counts and benefit IDs for editorial review; it does not silently rewrite articles or upgrade a stale support program to `open`.
- Popular benefit selection needs genuine source view-count data where available, official application status and expiry validation. No fabricated click/search-volume rankings, invented support sums or guesses about active application windows.
- News/trends are insufficient alone; source dates, audience eligibility, region and application deadlines must be checked against official agencies before content changes.

## 3. SEO and AdSense readiness

- Existing `tools/verify_release.py` already checks every advertised sitemap URL for canonical/metadata/H1/indexability and structured breadcrumbs. Preserve that audit; add the freshness evidence to the existing verification CI rather than launching a second crawl.
- Flag human-review-needed pages; do not mass-index uncertain application pages or add unverified structured data.
- Privacy, About, Contact, Terms, helpful original explanations and mobile clarity require human review. Search Console and AdSense approval status are **not** inferable from a passing CI run.
- No ads, consent scripts, external tracking, platform application or changes to the public site are made by this Draft PR. All activation requires separate approval.
