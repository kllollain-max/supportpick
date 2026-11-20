# SupportPick Naver Draft Uploader v1

This module is intentionally isolated from SupportPick content generation and public-site deployment.

## Scope

CONTENT_READY -> NAVER_QUEUE -> LOCK_ACQUIRED -> PRECHECK -> EDITOR_OPEN -> TITLE_DONE -> BODY_DONE -> IMAGE_DONE -> FORMAT_DONE -> PRE_SAVE_VALIDATED -> SAVE_INTENT -> SAVE_CLICKED -> DRAFT_FOUND -> REOPENED -> CONTENT_VERIFIED -> VERIFIED

Success is **VERIFIED only**. SAVE_CLICKED or a toast message is never final success.

## Safety invariants

- One content item at a time.
- Never overwrite an unknown editor draft.
- Never retry a SAVE_STATUS_UNKNOWN item by creating a fresh post before draft lookup.
- Never bypass CAPTCHA, MFA, security checks, account restrictions, or explicit user verification.
- Never auto-publish during Phase 1-3.
- Content generation artifacts are immutable inputs; uploader failure never deletes them.
- Persistent browser tab IDs are forbidden; each run rediscovers the active editor.
- Logs must not contain passwords, cookies, session tokens, or personal authentication data.

## Input contract

Create one JSON manifest per content item:

```json
{
  "content_id": "supportpick-YYYYMMDD-NNN",
  "title": "...",
  "body_text": "...",
  "images": [
    {"path": "...", "slot": "hero"},
    {"path": "...", "slot": "core"},
    {"path": "...", "slot": "check"}
  ],
  "cta_text": "다른 생활 지원 제도는 지원금픽 링크에서 확인하세요.",
  "cta_url": "https://kllollain-max.github.io/supportpick/"
}
```

Runtime state and the execution ledger are stored outside generated content.

## Phased rollout

1. Phase 1: exactly 1 real new article, draft-only, must reach VERIFIED.
2. Phase 2: 3 sequential real articles, each VERIFIED before next starts.
3. Phase 3: 5 sequential real articles, same invariant.
4. Only after all phases pass may the queue be attached to normal daily throughput.

Auto-publish remains disabled unless separately approved.
