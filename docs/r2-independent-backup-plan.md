# SupportPick R2-independent recovery plan (draft; no production writes)

Status: proposal only. Owner approval required before changing schedules, storage destinations, secrets, merging, or deploying. Cloudflare R2 account recovery remains on hold.

## Current observed recovery boundary (2026-11-09 KST)

- The `supportpick-operations.yml` workflow restores the latest completed main-branch operations artifact, then verifies a generation pointer and content before promoting it.
- A recovery bundle holds current + previous validated generations. The 2026-11-09 run 42527504841 reported `generations: 2`, `sourcePreserved: true`.
- Existing run artifact 13635897623 expires 2026-11-12 07:03 KST. Changing retention in a future workflow **does not extend this existing artifact**.
- This PR proposes 7-day retention for future `supportpick-runtime-state` and 1-day retention for large collection evidence to contain storage growth; organization/repository maximum retention limits may supersede them. Existing artifacts retain their original expiry. At two runs/day and the observed 21.45 MB state + 18.40 MB evidence sizes, estimated steady-state storage attributable to these two types is about 337 MB (7 × 2 × 21.45 + 1 × 2 × 18.40), **before all other artifacts**, and is not a guarantee of free-quota compliance.
- GitHub Actions artifacts are **not independent long-term backups**: they can expire, be deleted, or become inaccessible together with the repository/account.

## Proposed layered retention (not yet implemented)

1. **Live recovery layer:** keep validated current + previous generations in Actions artifacts with verified SHA-256, generation ID, manifest and source metadata. Preserve existing restore's fail-closed behavior.
2. **Independent backup layer:** after owner selects a *separately controlled* destination, export a signed/checksummed, immutable time-stamped archive. Prefer a different provider/account with least-privilege write-only automation credentials and independent read credentials. No API keys, session tokens, personal data or GitHub Secrets in archive. Avoid committing bulk backups to the public repository.
3. **Retention recommendation:** maintain at least 7 daily + 4 weekly + 3 monthly recovery points, subject to actual costs, storage limits and owner approval. Prevent automatic pruning from removing the last known-good full snapshot.
4. **Verification:** after each export, independently read metadata/hash and ensure archive includes validated manifest, both generation directories when available, application/workflow configuration (redacted), and explicit restoration instructions. Report failures separately from public site status; never label an unverified upload `backup_success`.
5. **Restore drill:** download a chosen archive into an isolated directory; verify checksum and schema, run `read_current` and `tools/build.py` without production deployment, assert ID counts and source preservation, then compare output manifest to recorded source. Exercise both healthy and corrupted/tampered archive paths.
6. **Recovery authority:** manual owner approval before copying restored data onto production, moving refs, changing Pages, or enabling automatic publishing. Document last-good SHA, generation ID, RTO/RPO observation and rollback method.

## Pre-implementation acceptance checklist

- [ ] Destination and credentials explicitly approved; recovery succeeds even when R2 is unavailable.
- [ ] Storage quotas, estimated size per snapshot, lifecycle and actual billing reviewed.
- [ ] Archive content inventory excludes secrets/PII; checksums checked after retrieval.
- [ ] At least one **real isolated restore** passes against a stored archive, not just unit tests or a simulated fixture.
- [ ] Corruption, missing latest archive, stale generation and limited permissions produce safe failure with alert.
- [ ] Existing operations schedule, approval gates, Threads publication ledger and current site remain unchanged.
- [ ] A dedicated Draft PR documents CI evidence and required approval before main merge.

## Operational warning

If the latest completed operations run loses its artifact, `restore_latest_state.py` intentionally refuses to fall back blindly to stale data. Do **not** loosen this safety check to make jobs appear green. Protect and extend artifact availability first, and only add a documented, verified independent recovery source after testing.
