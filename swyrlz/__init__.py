from pathlib import Path
import shutil

_RUNTIME_LIVE = Path("/tmp/swrlz-admin/live")
_RUNTIME_LIVE.mkdir(parents=True, exist_ok=True)
_BUNDLED_GATE5 = Path(__file__).with_name("gate5_live.py")
_LIVE_GATE5 = _RUNTIME_LIVE / "gate5_live.py"

# Preserve a hot-edited runtime copy when present; seed only on a fresh runtime.
if not _LIVE_GATE5.exists() and _BUNDLED_GATE5.is_file():
    shutil.copy2(_BUNDLED_GATE5, _LIVE_GATE5)
