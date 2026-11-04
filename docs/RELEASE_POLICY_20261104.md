# Unchanged public release guard

Collection still runs at the original cadence and preserves every validated current/previous raw generation. A same-day deployment is skipped only when the content fingerprint matches the published release and four existing public files match that release's SHA-256 hashes. First use, network uncertainty, missing metadata or a corrupt public file requires the ordinary validated deployment path.

The fingerprint includes official content and views, source modification dates, verification/hold results, blog/guide registry, previous IDs, failure status, build code and static assets. It excludes collection-only clocks and generation identifiers. A new Korean calendar day also requires a rebuild so displayed query times and time-sensitive states cannot age indefinitely. Guide expiry or other detected hold changes also require a release.

On a skipped release, the public generation and its real query time remain unchanged. The newer raw generation is retained separately for subsequent runs; it is never reported as publicly deployed. The publish-decision artifact records both identities and probe outcomes. Sitemap lastmod continues to use content/official modification evidence, not collection time. Manual explicitly approved deployments remain possible.

Rollback: revert this change and redeploy without resetting collected data, records or other automation.

## Concurrent editorial protection

During the integrated task the existing blog sync published a fifth matching article while an older explicitly approved deployment was starting. That older run was canceled before deployment, preserving the new link. Both manual and collection deployments now recheck the approved checkout against remote main immediately before publication; a stale checkout fails without removing the current public site. Manual deployments also check before building. Collection bundles are retained before the final guard, so a following deployment of current main can restore the newly collected state. A real isolated git integration test advances remote main between the two checks and verifies that the old checkout is rejected and the rebuilt current checkout passes. Deliberate rollback remains possible by reverting the relevant change on current main.
