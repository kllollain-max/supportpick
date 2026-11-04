# Searchable benefit documents and editorial review

Authorized scope: the owner's 2026-11-04 integrated implementation instruction, including merge, GitHub Pages deployment, and Search Console resubmission after validation. No advertising code or new Naver publishing action is included.

## Actual problem and implementation

The previous application exposed benefit screens only through fragments. Its sitemap contained three independently served pages. Valid XML and HTTP 200 did not establish that Search Console had fetched or indexed it; the observed report still said it could not fetch. Google's live URL test had succeeded. No specific HTTP/XML/property mismatch was established, so the Google report error is not represented as a repaired server error.

The public build now creates benefits/<service-ID>/index.html for every current ID, with the core source information present in the response HTML. Real anchors connect application cards, the paginated directory, related benefits, and the homepage's twenty discovery links. Old #benefit= links resolve to the corresponding document. Search conditions/scroll position remain in the same session store; record keys, format, recovery copy, conflict checks, notes and preferences are unchanged. detail.js uses the existing core.js store instead of a separate record format.

The build checks path safety and case-folded collisions, nested links, metadata, indexing policy, and secret patterns. The generated sitemap includes only complete, nonduplicate, unheld documents plus the five information pages and directory pages. Actual source modification dates and deliberate template/editorial revision dates are used for lastmod. Data query/collection time is not used as content modification time. The entire advertised set is inspected before deployment. After deployment the workflow verifies the actual source revision, data generation, HTTP 200, initial HTML, canonical, metadata, BreadcrumbList, and content hash of every served HTML document.

## Content and review

The immutable API source remains the factual basis. No additional API collection, social publishing, account credential or automation setting is changed by this work.

Every valid detail provides the source fields, dates, official links, conditional preparation guidance, and related records. guides.json contains twenty individually written explanations selected from actual serviceList.조회수, after excluding expired rounds, unconfirmed new enrollment and conflicting current conditions. The source edition, review scope, official references and review timestamps are recorded. Missing counts are not estimated. Current application availability is not certified merely from an API response or a future deadline.

A material hash binds each rich explanation to its exact source facts; query timestamps, generation IDs and popularity counts do not invalidate unchanged content. A change to its facts, expiry, ambiguous duplicate review, or invalid reference withholds that rich explanation and keeps the current source/preparation guidance. Seven specifically identified records have their detailed body and indexing withheld pending review, with a holding notice and links to the official authority. Loan amounts, interest and changed account conditions are not republished as current facts on those holding documents. The holds are intentional; clearing one requires an actual new source review.

Existing blog matching remains exact by service ID, source edition, region/year/round, confirmed publication and expiry. It is rendered at the bottom of the matching document. Stale/unpublished/ambiguous links are hidden. Threads is not added to the website.

Multiple application rounds are no longer collapsed into a misleading single interval. The original source period text remains visible. Ended source intervals are labeled as elapsed rather than currently open.

## Deletions and recovery

A service missing from the current but present in the previous retained generation gets a noindex holding document. Older unknown addresses receive GitHub Pages' real 404 with the custom 404.html. Neither case deletes stored application or interest records. A valid collection snapshot remains required. Collection failure retains the last validated data and shows a failure/delay notice. Build or release validation failure prevents the Pages upload/deploy steps. Existing Git history, the prior deployed artifact and current/previous runtime-state backups remain the recovery path. For the pre-change rollback, select backup/pre-search-detail-20261104 as the workflow ref as well as its approved source SHA, so the old workflow does not call new tools missing from the old checkout. Restore its latest validated state; do not replace records or initialize a new store.

## robots.txt and console boundaries

Robots directives apply at https://kllollain-max.github.io/robots.txt, not /supportpick/robots.txt. Both previously returned 404; absent robots.txt is not itself a crawl prohibition. This project must not change the domain root or affect CareerPick/other projects. No ineffective subdirectory robots file is advertised as a fix. Any later root robots change must preserve other projects and requires appropriate root repository scope.

The Google URL-prefix property is https://kllollain-max.github.io/supportpick/. Ownership is verified. Homepage indexing was requested and accepted, which is not proof of indexing. After deployment submit the changed sitemap once, record its actual report status separately, and do not loop requests. Naver verification remains unset; SEO readiness does not mean Naver registration is complete.

The site now has introduction/source, privacy, service-use and public correction/contact pages. It clearly identifies its independent operator and official application destinations. No AdSense code, application, policy acceptance, or approval guarantee is included.

## Asset cache and transient transport checks

CSS, JavaScript and image URLs receive a version derived from their actual SHA-256 bytes. HTML canonical/navigation addresses and record keys remain unchanged. This prevents previously cached assets from being mixed with new documents. A public browser had retained the old CSS while the server already served the new stylesheet; the computed detail width and H1 did not match the new rules. The correction is verified in the same browser after deployment.

The first full public pass fetched 11,057 HTML documents; two requests returned HTTP 503 while the other 11,055 passed. The network verifier now retries each transient transport/408/429/5xx response once, sequentially after the full pass, and records the initial failure and actual recovery. Persistent failure, HTTP 404, content hash and metadata mismatches remain failures. No result is marked successful without a real valid response.
