"""Hot R39 entrypoint v49."""
from __future__ import annotations
import urllib.request
_SOURCE_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/6361684a82f8ce54b62d25b5dbeb9d75f99bdca8/runtime_hot/r39_engine_v49.py"
_request = urllib.request.Request(_SOURCE_URL, headers={"User-Agent": "swrlz-r39-v49-loader"})
with urllib.request.urlopen(_request, timeout=20) as _response:
    _source = _response.read(4000001)
if len(_source) > 4000000:
    raise RuntimeError("R39_V49_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _SOURCE_URL, "exec"), globals(), globals())
