from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

SESSION_COOKIE = "swrlz_session"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60
DEFAULT_GOOGLE_CLIENT_ID = "1083208613166-bj7isingvbv5dcns9ldtru8cjfj993mc.apps.googleusercontent.com"
RETIRED_GOOGLE_CLIENT_IDS = {
    "1083208613166-59am0s2p1v4vpoc04klr3iinh0oph1en.apps.googleusercontent.com",
}


class AccountConfigurationError(RuntimeError):
    pass


class AuthenticationError(PermissionError):
    pass


@dataclass(frozen=True)
class VerifiedGoogleIdentity:
    subject: str
    email: str | None
    email_verified: bool
    name: str | None
    picture: str | None


def google_client_id() -> str:
    configured = os.environ.get("SWRLZ_GOOGLE_CLIENT_ID", "").strip()
    # Migrate the one known-bad OAuth identifier that was introduced during the
    # browser compatibility work. This keeps production healthy even when an old
    # Vercel environment value survives after the source repair.
    if not configured or configured in RETIRED_GOOGLE_CLIENT_IDS:
        return DEFAULT_GOOGLE_CLIENT_ID
    return configured


def _session_secret_material() -> tuple[str, str]:
    explicit = os.environ.get("SWRLZ_SESSION_SECRET", "").strip()
    if len(explicit) >= 32:
        return explicit, "SWRLZ_SESSION_SECRET"
    for key in ("SWRLZ_ADMIN_TOKEN", "SWRLZ_WEB_CHAT_TOKEN"):
        value = os.environ.get(key, "").strip()
        if value:
            return value, key
    return "", ""


def session_secret_source() -> str:
    return _session_secret_material()[1]


def session_secret() -> bytes:
    value, source = _session_secret_material()
    if not value:
        raise AccountConfigurationError("No server-side account session secret source is configured")
    if source == "SWRLZ_SESSION_SECRET":
        return value.encode("utf-8")
    # Domain-separate an already configured server secret instead of reusing it directly.
    return hashlib.sha256(("swrlz-account-session-v1\x00" + value).encode("utf-8")).digest()


def auth_configured() -> bool:
    value, _ = _session_secret_material()
    return bool(google_client_id() and value)


def verify_google_credential(credential: str) -> VerifiedGoogleIdentity:
    client_id = google_client_id()
    if not client_id:
        raise AccountConfigurationError("SWRLZ_GOOGLE_CLIENT_ID is not configured")
    token = str(credential or "").strip()
    if not token:
        raise AuthenticationError("Google credential is required")
    try:
        claims = google_id_token.verify_oauth2_token(token, google_requests.Request(), client_id)
    except Exception as exc:
        raise AuthenticationError("Google ID token verification failed") from exc
    issuer = str(claims.get("iss") or "")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        raise AuthenticationError("Google token issuer is invalid")
    subject = str(claims.get("sub") or "").strip()
    if not subject:
        raise AuthenticationError("Google token is missing subject")
    return VerifiedGoogleIdentity(
        subject=subject,
        email=str(claims.get("email")) if claims.get("email") else None,
        email_verified=claims.get("email_verified") is True,
        name=str(claims.get("name")) if claims.get("name") else None,
        picture=str(claims.get("picture")) if claims.get("picture") else None,
    )


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * ((4 - len(text) % 4) % 4))


def issue_session(user_id: str, *, ttl_seconds: int = SESSION_TTL_SECONDS, claims: dict[str, Any] | None = None) -> str:
    now = int(time.time())
    body: dict[str, Any] = {
        "v": 1,
        "sub": str(user_id),
        "iat": now,
        "exp": now + max(300, min(int(ttl_seconds), 30 * 24 * 60 * 60)),
    }
    if isinstance(claims, dict):
        safe: dict[str, Any] = {}
        for key in ("provider", "providerSubject", "email", "emailVerified", "name", "picture", "durable"):
            value = claims.get(key)
            if isinstance(value, (str, bool)) or value is None:
                safe[key] = value
        if safe:
            body["identity"] = safe
    encoded = _b64(json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature = _b64(hmac.new(session_secret(), encoded.encode("ascii"), hashlib.sha256).digest())
    return encoded + "." + signature


def verify_session(token: str | None) -> dict[str, Any]:
    value = str(token or "").strip()
    if not value or "." not in value:
        raise AuthenticationError("session is missing")
    encoded, supplied = value.rsplit(".", 1)
    expected = _b64(hmac.new(session_secret(), encoded.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(supplied, expected):
        raise AuthenticationError("session signature is invalid")
    try:
        body = json.loads(_unb64(encoded))
    except Exception as exc:
        raise AuthenticationError("session payload is invalid") from exc
    now = int(time.time())
    if body.get("v") != 1 or not str(body.get("sub") or "") or int(body.get("exp") or 0) <= now:
        raise AuthenticationError("session is expired or invalid")
    return body


def user_id_from_request(request) -> str:
    body = verify_session(request.cookies.get(SESSION_COOKIE))
    return str(body["sub"])
