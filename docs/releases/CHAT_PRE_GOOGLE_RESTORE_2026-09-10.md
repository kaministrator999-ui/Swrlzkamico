# Chat pre-Google restore

The live Chat source branch `runtime` has been intentionally moved back to commit `64c53999aa374c589bf2692e12db57ca133ab21c`, the exact parent immediately before the Google-account/durable-user-state feature commit `c9a6ab4eb38e93080f02d557f5c2a7a058cc1efd`.

A backup branch `runtime-pre-google-revert-backup` preserves the previous runtime head `d964b5ed22167c90b8c2d4792ae7f4bd6e8f7ed5` for recovery.

This marker exists only to trigger a fresh production build so the live page-runtime cache is recreated against the restored Chat source.
