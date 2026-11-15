"""Private, Google-owner-authenticated Aiven meter for the active HF Station.

Routes are installed explicitly; importing this module changes nothing.
Aiven is never contacted during public Chat requests or automatic page loads.
"""
from __future__ import annotations

import asyncio
import hmac
import json
import math
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

HEADERS = {
    "Cache-Control": "private, no-store, max-age=0",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}
METRIC_NAMES = (
    "cpu_usage", "disk_usage", "disk_ioread", "disk_iowrites",
    "load_average", "mem_usage", "net_receive", "net_send",
)
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
SAFE_TEXT = re.compile(r"^[\w .:%/()=+@-]{0,120}$")
PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>§wyrlz · Private Aiven Metrics</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}
body{margin:0;padding:16px;background:#070d19;color:#e6f2ff;font:15px/1.5 system-ui,sans-serif}
main{width:min(820px,100%);margin:24px auto}h1{font-size:1.7rem}
p{color:#a9bdd0}a{color:#7ee9ff}button{border:1px solid #4578a5;border-radius:10px;background:#133453;color:#fff;padding:10px 16px;font:inherit;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:10px}
.card{background:#0e1d31;border:1px solid #274966;border-radius:12px;padding:13px}
.label{font-size:.8rem;color:#a5bdd1}.value{font-weight:700;font-size:1.2rem;overflow-wrap:anywhere}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#0b1526;border:1px solid #28425b;border-radius:10px;padding:12px;max-height:260px;overflow:auto}
</style></head>
<body><main><h1>Aiven · System Health</h1>
<p>Private administrator view. Read-only metrics are requested only when you press Check Aiven; public chat never loads this data.</p>
<button type="button" id="check">Check Aiven</button>
<a href="https://console.aiven.io/" rel="noopener noreferrer" target="_blank">Aiven Console and alerts</a>
<p id="status" role="status">Ready. Your Google session is required.</p>
<div class="grid" id="summary"></div><pre id="metrics" aria-label="Aiven metrics">No metrics requested.</pre>
</main><script>
const check=document.getElementById('check'),status=document.getElementById('status'),
summary=document.getElementById('summary'),metrics=document.getElementById('metrics');
function card(name,value){const item=document.createElement('section');item.className='card';
const label=document.createElement('div');label.className='label';label.textContent=name;
const text=document.createElement('div');text.className='value';text.textContent=value;
item.append(label,text);summary.append(item);}
check.addEventListener('click',async()=>{
check.disabled=true;summary.replaceChildren();status.textContent='Checking Aiven…';
try{const r=await fetch('/api/admin/aiven/metrics',{credentials:'same-origin',cache:'no-store'});
const j=await r.json();if(!r.ok||!j.ok){status.textContent=j.message||j.code||('HTTP '+r.status);metrics.textContent='No readings available.';return;}
status.textContent='Read '+new Date(j.checkedAt*1000).toLocaleString()+' · last hour · read-only';
const s=j.service||{};card('Service',s.name||'Unavailable');card('State',s.state||'Unavailable');
card('Plan',s.plan||'Unavailable');card('Provisioned disk',s.diskCapacityMB==null?'Unavailable':s.diskCapacityMB+' MB');
metrics.textContent=JSON.stringify(j.metrics,null,2);
}catch(e){status.textContent='Unable to load metrics.';metrics.textContent='Network error.'}
finally{check.disabled=false;}
});
</script></body></html>"""


def _authorized(user: dict | None) -> bool:
    """Require the signed-in Google identity, never the public display name."""
    if not isinstance(user, dict):
        return False
    subject = os.environ.get("SWRLZ_ADMIN_GOOGLE_SUB", "").strip()
    owner_email = os.environ.get("SWRLZ_ADMIN_GOOGLE_EMAIL", "").strip().casefold()
    if not (subject or owner_email):
        return False  # fail closed until the private owner allowlist is configured
    actual_sub = str(user.get("id") or "")
    actual_email = str(user.get("email") or "").strip().casefold()
    if subject and not hmac.compare_digest(actual_sub, "google:" + subject):
        return False
    if owner_email and (
        user.get("emailVerified") is not True
        or not hmac.compare_digest(actual_email, owner_email)
    ):
        return False
    return True


def _safe(value, depth=0):
    if depth > 6:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value if math.isfinite(value) else None
    if isinstance(value, str):
        return value if SAFE_TEXT.fullmatch(value) else None
    if isinstance(value, list):
        return [_safe(item, depth + 1) for item in value[-128:]]
    if isinstance(value, dict):
        output = {}
        for key, item in list(value.items())[:24]:
            if not isinstance(key, str) or not SAFE_TEXT.fullmatch(key):
                continue
            if re.search(r"secret|password|token|key|uri|host|address|credential", key, re.I):
                continue
            output[key] = _safe(item, depth + 1)
        return output
    return None


def _request(method: str, endpoint: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        "https://api.aiven.io/v1" + endpoint,
        data=data, method=method,
        headers={
            "Authorization": "aivenv1 " + token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SWRLZ-Private-Aiven-Metrics/1",
        },
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        raw = response.read(262145)
    if len(raw) > 262144:
        raise ValueError("AIVEN_RESPONSE_TOO_LARGE")
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("AIVEN_RESPONSE_INVALID")
    return result


def read_metrics() -> dict:
    token = os.environ.get("SWRLZ_AIVEN_API_TOKEN", "").strip()
    project = os.environ.get("SWRLZ_AIVEN_PROJECT", "").strip()
    service = os.environ.get("SWRLZ_AIVEN_SERVICE", "").strip()
    if not (token and project and service):
        return {"ok": False, "code": "AIVEN_NOT_CONFIGURED",
                "message": "Aiven connection is not configured in the Space's private secrets."}
    if not (SAFE_NAME.fullmatch(project) and SAFE_NAME.fullmatch(service)):
        return {"ok": False, "code": "AIVEN_CONFIG_INVALID"}
    path = "/project/" + urllib.parse.quote(project, safe="") + "/service/" + urllib.parse.quote(service, safe="")
    try:
        info = _request("GET", path, token).get("service") or {}
        data = _request("POST", path + "/metrics", token, {"period": "hour"})
        metrics = data.get("metrics") or {}
        if not isinstance(info, dict) or not isinstance(metrics, dict):
            return {"ok": False, "code": "AIVEN_RESPONSE_INVALID"}
        disk = info.get("disk_space_mb")
        return {
            "ok": True, "checkedAt": int(time.time()), "source": "Aiven",
            "service": {
                "name": service,
                "state": str(info.get("state") or "")[:40],
                "plan": str(info.get("plan") or "")[:80],
                "type": str(info.get("service_type") or "")[:40],
                "diskCapacityMB": disk if type(disk) is int and disk >= 0 else None,
            },
            "metrics": {name: _safe(metrics[name]) for name in METRIC_NAMES if name in metrics},
        }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "code": "AIVEN_HTTP_ERROR", "httpStatus": exc.code}
    except (urllib.error.URLError, OSError, TimeoutError):
        return {"ok": False, "code": "AIVEN_UNREACHABLE"}
    except (ValueError, TypeError):
        return {"ok": False, "code": "AIVEN_RESPONSE_INVALID"}


def install(app, account_session):
    """Integrate into the existing Google-authenticated HF Station, not Chat UI."""
    def owner(request: Request) -> bool:
        _, user = account_session(request)
        return _authorized(user)

    @app.get("/admin/aiven", include_in_schema=False)
    async def private_aiven_page(request: Request):
        if not owner(request):
            return HTMLResponse("Not found", status_code=404, headers=HEADERS)
        headers = dict(HEADERS)
        headers["Content-Security-Policy"] = (
            "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
            "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
        )
        return HTMLResponse(PAGE, headers=headers)

    @app.get("/api/admin/aiven/metrics", include_in_schema=False)
    async def private_aiven_metrics(request: Request):
        if not owner(request):
            return JSONResponse({"ok": False, "code": "ADMIN_ACCESS_DENIED"},
                                status_code=403, headers=HEADERS)
        result = await asyncio.to_thread(read_metrics)
        return JSONResponse(result, status_code=200 if result.get("ok") else 503,
                            headers=HEADERS)
