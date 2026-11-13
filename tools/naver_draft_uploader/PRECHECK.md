# Phase-1 live precheck checklist

A real Naver browser run may start only when every item below is confirmed.

## Environment
- Browser automation runtime starts successfully.
- Network is stable enough to load Naver.
- One supported browser is selected for the run.
- No previous browser tab ID is reused from an older run.

## Identity
- Signed-in Naver account is visible.
- Blog identity is exactly bible_el.
- No account switch is pending.
- No CAPTCHA, MFA, additional verification, restriction, or security warning is present.

Any authentication or restriction screen => MANUAL_AUTH_REQUIRED and stop.

## Editor
- Fresh current tabs are enumerated.
- The editor is rediscovered from the current browser state.
- Title field is visible and interactable.
- Body editor is visible and interactable.
- Photo upload UI is visible and interactable.
- Temporary-save control is visible.
- Toolbar is present.
- Existing editor content is inspected before any destructive action.

Unexpected existing content => FOREIGN_DRAFT_DETECTED or EXISTING_UNVERIFIED_DRAFT and stop.

## Content
- Manifest content_id is unique.
- Original article and images remain preserved outside Naver.
- Approved SupportPick CTA text and URL are present.
- All planned image files exist and are non-empty.
- No other brand CTA appears in the manifest.

## Save safety
- SAVE_INTENT is written before clicking temporary save.
- SAVE_CLICKED is never treated as success.
- If browser state is lost after save intent/click, the next action is draft lookup.
- New content input is forbidden while save outcome is unknown.

## Success
Only this sequence is success:

temporary save
→ draft list found
→ independent reopen
→ title verified
→ body verified
→ CTA verified
→ images verified
→ VERIFIED

Publishing is out of scope.
