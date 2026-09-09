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
    return os.environ.get("SWRLZ_GOOGLE_CLIENT_ID", "").strip()


def session_secret() -> bytes:
    value = os.environ.get("SWRLZ_SESSION_SECRET", "").strip()
    if len(value) < 32:
        raise AccountConfigurationError("SWRLZ_SESSION_SECRET must contain at least 32 characters")
    return value.encode("utf-8")


def auth_configured() -> bool:
    return bool(google_client_id() and len(os.environ.get("SWRLZ_SESSION_SECRET", "").strip()) >= 32)


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


def issue_session(user_id: str, *, ttl_seconds: int = SESSION_TTL_SECONDS) -> str:
    now = int(time.time())
    body = {
        "v": 1,
        "sub": str(user_id),
        "iat": now,
        "exp": now + max(300, min(int(ttl_seconds), 30 * 24 * 60 * 60)),
    }
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
