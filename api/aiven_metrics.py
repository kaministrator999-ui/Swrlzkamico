"""Read-only, on-demand Aiven service metrics for the protected admin workbench.

Nothing is polled from Chat, no credentials are returned to the browser, and
this module never mutates an Aiven service. The provider Console remains the
source of truth for alerts and complete time-series charts.
"""
from __future__ import annotations

import json
import math
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any

_API_ROOT = "https://api.aiven.io/v1"
_MAX_BYTES = 256 * 1024
_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_SAFE_LABEL = re.compile(r"^[\w .:%/()=+@-]{0,120}$")
_SECRET_FIELD = re.compile(r"password|token|secret|key|credential|authorization|uri|hostname|ip_address|service_host", re.I)


def _configuration() -> tuple[str, str, str] | None:
    token = os.environ.get("SWRLZ_AIVEN_API_TOKEN", "").strip()
    project = os.environ.get("SWRLZ_AIVEN_PROJECT", "").strip()
    service = os.environ.get("SWRLZ_AIVEN_SERVICE", "").strip()
    if not (token and project and service):
        return None
    if not (_SAFE_NAME.fullmatch(project) and _SAFE_NAME.fullmatch(service)):
        raise ValueError("INVALID_AIVEN_SERVICE_CONFIGURATION")
    return token, project, service


def _fetch(method: str, endpoint: str, token: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    encoded = json.dumps(body, separators=(",", ":")).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        _API_ROOT + endpoint,
        data=encoded,
        method=method,
        headers={
            "Authorization": "aivenv1 " + token,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "SWRLZ-Admin-Metrics/1",
        },
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        payload = response.read(_MAX_BYTES + 1)
    if len(payload) > _MAX_BYTES:
        raise ValueError("AIVEN_METRICS_RESPONSE_TOO_LARGE")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("AIVEN_METRICS_INVALID_RESPONSE")
    return data


def _safe_metrics(value: Any, depth: int = 0) -> Any:
    """Bound numeric chart data and labels; reject potential secret-bearing fields."""
    if depth > 6:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value if math.isfinite(value) else None
    if isinstance(value, str):
        return value if _SAFE_LABEL.fullmatch(value) else None
    if isinstance(value, list):
        return [_safe_metrics(item, depth + 1) for item in value[-32:]]
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for key, item in list(value.items())[:64]:
            if not isinstance(key, str) or len(key) > 90 or _SECRET_FIELD.search(key):
                continue
            projected = _safe_metrics(item, depth + 1)
            if projected is not None:
                out[key] = projected
        return out
    return None


def read_aiven_metrics() -> dict[str, Any]:
    """Fetch only on explicit authenticated admin request; never background-poll."""
    try:
        config = _configuration()
        if config is None:
            return {
                "ok": False, "configured": False, "code": "AIVEN_NOT_CONFIGURED",
                "message": "Set SWRLZ_AIVEN_API_TOKEN, SWRLZ_AIVEN_PROJECT and SWRLZ_AIVEN_SERVICE on the server.",
            }
        token, project, service = config
        segment = "/project/" + urllib.parse.quote(project, safe="") + "/service/" + urllib.parse.quote(service, safe="")
        info = _fetch("GET", segment, token)
        service_info = info.get("service") if isinstance(info.get("service"), dict) else {}
        metrics = _fetch("POST", segment + "/metrics", token, {"period": "hour"})
        return {
            "ok": True,
            "configured": True,
            "provider": "Aiven",
            "checkedAt": int(time.time()),
            "service": {
                "name": service,
                "project": project,
                "state": str(service_info.get("state") or "")[:40],
                "plan": str(service_info.get("plan") or "")[:80],
                "type": str(service_info.get("service_type") or "")[:40],
                "diskCapacityMB": service_info.get("disk_space_mb") if isinstance(service_info.get("disk_space_mb"), int) else None,
            },
            "metricsPeriod": "hour",
            "metrics": _safe_metrics(metrics.get("metrics") or {}),
            "note": "Provider readings are not billing quota forecasts. For alerts and graphs, use the Aiven Console.",
        }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "configured": True, "code": "AIVEN_HTTP_ERROR", "httpStatus": exc.code}
    except (urllib.error.URLError, TimeoutError, OSError):
        return {"ok": False, "configured": True, "code": "AIVEN_UNREACHABLE"}
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        code = str(exc)
        return {"ok": False, "configured": True, "code": code if code.startswith("AIVEN_") or code.startswith("INVALID_AIVEN_") else "AIVEN_INVALID_DATA"}
