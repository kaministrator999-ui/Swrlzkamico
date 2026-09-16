"""Hot R39 entrypoint v51."""
from __future__ import annotations
import urllib.request
_SOURCE_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/a30e2f53df0cbe421ee67e9de40d24a999f9bb17/runtime_hot/r39_engine_v51.py"
_request = urllib.request.Request(_SOURCE_URL, headers={"User-Agent": "swrlz-r39-v51-loader"})
with urllib.request.urlopen(_request, timeout=20) as _response:
    _source = _response.read(4000001)
if len(_source) > 4000000:
    raise RuntimeError("R39_V51_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _SOURCE_URL, "exec"), globals(), globals())
