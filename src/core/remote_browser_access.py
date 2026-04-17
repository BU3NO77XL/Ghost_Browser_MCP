"""Remote browser access metadata for manual login flows."""

import hmac
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urljoin


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class RemoteBrowserAccessConfig:
    enabled: bool
    public_url: str
    viewer_path: str
    token_secret: str
    token_ttl_seconds: int


def get_remote_browser_access_config() -> RemoteBrowserAccessConfig:
    return RemoteBrowserAccessConfig(
        enabled=_env_bool("GHOST_REMOTE_VIEWER_ENABLED"),
        public_url=os.environ.get("GHOST_REMOTE_VIEWER_PUBLIC_URL", "").strip(),
        viewer_path=os.environ.get("GHOST_REMOTE_VIEWER_PATH", "/vnc.html").strip() or "/vnc.html",
        token_secret=os.environ.get("GHOST_REMOTE_VIEWER_TOKEN_SECRET", "").strip(),
        token_ttl_seconds=max(60, _env_int("GHOST_REMOTE_VIEWER_TOKEN_TTL_SECONDS", 900)),
    )


def _sign_token(instance_id: str, expires_at: int, secret: str) -> str:
    payload = f"{instance_id}:{expires_at}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), payload, sha256).hexdigest()


def verify_remote_login_token(instance_id: str, expires_at: int, token: str) -> bool:
    config = get_remote_browser_access_config()
    if not config.token_secret:
        return False
    if expires_at < int(datetime.now(timezone.utc).timestamp()):
        return False
    expected = _sign_token(instance_id, expires_at, config.token_secret)
    return hmac.compare_digest(expected, token)


def build_remote_login_access(instance_id: str) -> Optional[Dict[str, Any]]:
    """Return optional noVNC metadata for a browser instance."""
    config = get_remote_browser_access_config()
    if not config.enabled or not config.public_url:
        return None

    expires_at_dt = datetime.now(timezone.utc) + timedelta(seconds=config.token_ttl_seconds)
    expires_at = int(expires_at_dt.timestamp())
    query = {
        "instance_id": instance_id,
        "expires": str(expires_at),
    }
    if config.token_secret:
        query["token"] = _sign_token(instance_id, expires_at, config.token_secret)

    base = config.public_url.rstrip("/") + "/"
    path = config.viewer_path.lstrip("/")
    login_url = urljoin(base, path)
    separator = "&" if "?" in login_url else "?"
    login_url = f"{login_url}{separator}{urlencode(query)}"

    return {
        "enabled": True,
        "type": "novnc",
        "url": login_url,
        "expires_at": expires_at_dt.isoformat(),
        "expires_in_seconds": config.token_ttl_seconds,
        "requires_token": bool(config.token_secret),
    }
