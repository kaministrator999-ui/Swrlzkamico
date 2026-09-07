from __future__ import annotations

import shutil
from pathlib import Path


def install() -> None:
    """Seed the 2.1.8 index, then stop legacy hot helpers from overwriting it."""
    import api.runtime_hot as hot

    runtime_index = Path("/tmp/swrlz-admin/web/index.html")
    bundled_index = Path(__file__).resolve().parents[1] / "runtime_pages" / "index.html"
    runtime_index.parent.mkdir(parents=True, exist_ok=True)
    if bundled_index.is_file():
        shutil.copy2(bundled_index, runtime_index)

    def ensure_index() -> None:
        runtime_index.parent.mkdir(parents=True, exist_ok=True)
        if not runtime_index.is_file() and bundled_index.is_file():
            shutil.copy2(bundled_index, runtime_index)

    hot._ensure_portal = ensure_index
