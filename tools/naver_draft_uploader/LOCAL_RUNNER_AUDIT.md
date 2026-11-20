# 2026-11-11 local-runner audit and safe preparation

This supersedes earlier statements that only browser credit or independent reopen remained. The live uploader is NOT ready. Actual Naver VERIFIED count is zero.

## Reproduced / observed
- Exact original state_machine.py bytes matched Git blob `5c400f09cf7ba78b8743a7fb243a6ab17fe78ece` before testing.
- Extra producer metadata (`source_run_id`) raises TypeError in the old Manifest constructor.
- UTF-8 BOM JSON raises JSONDecodeError in the old loader.
- `/mnt/data/` paths cannot be reused on a user's Windows PC.
- Public blog URL was treated as proof of account ownership; generic contenteditable selection and file-chooser action counting were unsafe.
- Independent list/reopen is not implemented. Existing runner does not read its prior checkpoint before resetting it; queue/phase helper presence alone does not prove integration.
- DryRunAdapter still uses VERIFIED; these simulated records MUST NOT be used as live phase evidence.
- Legacy queue.py can shadow the Python standard-library queue module.

## Changes / containment
- Legacy live entry point and adapter are blocked before browser input. Scheduler registration is blocked before modifying any task.
- New `windows_starter` provides manual local login and read-only structural inspection. No fill/click/save/publish API is invoked.
- Starter is isolated with Python `-I`, uses an independent profile under LOCALAPPDATA, and does not import the legacy queue/runner.
- Portable package carries original TXT/3 PNG files with relative paths; its input parser accepts producer metadata and UTF-8 BOM.
- All four SHA-256 values were independently computed; all 3 images were verified and pixel-decoded. Original bytes were not changed.
- Public-page reachability is never PRECHECK_OK/account verification. Structural inspection is never VERIFIED.

## Actually run
26 starter unit tests PASS; 3 synthetic page scenarios PASS with Linux Chromium 144.0.7559.96 and Playwright 1.57.0. These are NOT live Naver tests or Windows CMD tests. Complete current legacy uploader suite was not run and is not claimed to pass.

## Remaining
Repair legacy manifest/queue/lock/restart integration; separate simulated/live receipts; implement authenticated ownership proof, actual image readback and independent reopen using observed UI; run actual sequential Phase 1, then 3, then 5. Keep generator and schedules unchanged, PR Draft and unmerged, auto-publish unavailable.

The supplied Windows ZIP is preparation/diagnostics, not a finished uploader. Do not charge a remote browser provider or enable a recurring task to work around these blockers.
