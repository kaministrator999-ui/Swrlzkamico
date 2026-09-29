# Hugging Face Space deployment request gate

This file is intentionally inert by default.

A future explicitly approved deployment is started by changing this file on `main` to a fresh request containing:

```text
TARGET=kamiloki/Swyrlz
APPROVED=1
SOURCE_REF=feature/hf-space-manual-deploy
REQUEST_NONCE=<fresh unique value for this approved deployment>
```

The `.github/workflows/hf-space-request.yml` push workflow validates the request and then calls the canonical HF deployment workflow. Editing any other source file does not trigger this deployment path.

Do not set `APPROVED=1` or change `REQUEST_NONCE` without explicit user approval for that deployment.
