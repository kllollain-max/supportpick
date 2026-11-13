# SupportPick content-generator integration contract

The existing SupportPick content generator remains the source of truth for article creation.
The uploader is a downstream consumer only.

## Producer responsibilities

When a SupportPick article is fully generated, create one immutable manifest and mark the content artifact as:

```
CONTENT_READY
```

The producer must not call Naver directly. It only hands off:

- content_id
- final title
- plain-text body
- ordered image paths
- approved SupportPick CTA text
- SupportPick URL
- original artifact locations

The uploader must never regenerate the article just because Naver input failed.

## Handoff

The producer may enqueue exactly one queue entry per content_id.

Duplicate enqueue returns:

```
DUPLICATE_QUEUE_ITEM
```

and must not create a second Naver editor task.

## Consumer responsibilities

The consumer processes one runnable queue item at a time.

No later queue item may begin until the current item reaches one of:

- VERIFIED
- MANUAL_REVIEW_REQUIRED
- MANUAL_AUTH_REQUIRED
- FOREIGN_DRAFT_DETECTED

RETRY_PENDING remains the same queue item and same content_id.

SAVE_STATUS_UNKNOWN is special: the next run must search Naver drafts before any new editor input.

## Success semantics

Only VERIFIED means success.

A report that says save_clicked=true, draft_found=true, or reopened=true but verified=false is not a successful draft upload.

## Production enablement

Production browser execution remains disabled until:

1. authenticated bible_el PRECHECK is possible;
2. one real new article reaches VERIFIED without publish;
3. Phase-1 gate passes;
4. three sequential real articles reach VERIFIED;
5. Phase-2 gate passes;
6. five sequential real articles reach VERIFIED;
7. Phase-3 gate passes.

Auto-publish is out of scope and must remain disabled.
