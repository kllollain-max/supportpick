# Unchanged public release guard

Collection still runs at the original cadence and preserves every validated current/previous raw generation. A same-day deployment is skipped only when the content fingerprint matches the published release and four existing public files match that release's SHA-256 hashes. First use, network uncertainty, missing metadata or a corrupt public file requires the ordinary validated deployment path.

The fingerprint includes official content and views, source modification dates, verification/hold results, blog/guide registry, previous IDs, failure status, build code and static assets. It excludes collection-only clocks and generation identifiers. A new Korean calendar day also requires a rebuild so displayed query times and time-sensitive states cannot age indefinitely. Guide expiry or other detected hold changes also require a release.

On a skipped release, the public generation and its real query time remain unchanged. The newer raw generation is retained separately for subsequent runs; it is never reported as publicly deployed. The publish-decision artifact records both identities and probe outcomes. Sitemap lastmod continues to use content/official modification evidence, not collection time. Manual explicitly approved deployments remain possible.

Rollback: revert this change and redeploy without resetting collected data, records or other automation.
