"""Hot-swappable R39 engine entrypoint.

Admin syncs this file from the non-deploying dev branch into
/tmp/swrlz-admin/runtime/hot/inference/r39_engine.py. Keep the public contract small:
ENGINE_ID, MODEL_SHA256, inspect_engine(), generate_events().
"""
from __future__ import annotations

import swyrlz.r39_matvec_patch  # noqa: F401
import swyrlz.r39_tokenizer_patch  # noqa: F401
from swyrlz.r39_inference import ENGINE_ID, MODEL_SHA256, generate_events, inspect_engine

HOT_REVISION = "2.1.7-bootstrap"
