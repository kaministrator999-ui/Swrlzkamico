"""Hot R39 entrypoint v44."""
from __future__ import annotations
import urllib.request
_SOURCE_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/2031e2dfcd998a24671796b948adadadd3f803ac/runtime_hot/r39_engine_v44.py"
_request = urllib.request.Request(_SOURCE_URL, headers={"User-Agent": "swrlz-r39-v44-loader"})
with urllib.request.urlopen(_request, timeout=20) as _response:
    _source = _response.read(4000001)
if len(_source) > 4000000:
    raise RuntimeError("R39_V44_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _SOURCE_URL, "exec"), globals(), globals())
