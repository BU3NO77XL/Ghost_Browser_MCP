"""Tests for remote browser access metadata."""

from urllib.parse import parse_qs, urlparse


def test_remote_browser_access_disabled_by_default(monkeypatch):
    from core.remote_browser_access import build_remote_login_access

    monkeypatch.delenv("GHOST_REMOTE_VIEWER_ENABLED", raising=False)
    monkeypatch.delenv("GHOST_REMOTE_VIEWER_PUBLIC_URL", raising=False)

    assert build_remote_login_access("instance-1") is None


def test_remote_browser_access_builds_signed_novnc_url(monkeypatch):
    from core.remote_browser_access import build_remote_login_access, verify_remote_login_token

    monkeypatch.setenv("GHOST_REMOTE_VIEWER_ENABLED", "true")
    monkeypatch.setenv("GHOST_REMOTE_VIEWER_PUBLIC_URL", "https://browser.example.com")
    monkeypatch.setenv("GHOST_REMOTE_VIEWER_TOKEN_SECRET", "test-secret")
    monkeypatch.setenv("GHOST_REMOTE_VIEWER_TOKEN_TTL_SECONDS", "600")

    access = build_remote_login_access("instance-1")

    assert access is not None
    assert access["type"] == "novnc"
    assert access["requires_token"] is True
    assert access["expires_in_seconds"] == 600

    parsed = urlparse(access["url"])
    query = parse_qs(parsed.query)
    expires = int(query["expires"][0])
    token = query["token"][0]

    assert parsed.scheme == "https"
    assert parsed.netloc == "browser.example.com"
    assert parsed.path == "/vnc.html"
    assert query["instance_id"] == ["instance-1"]
    assert verify_remote_login_token("instance-1", expires, token) is True
    assert verify_remote_login_token("other-instance", expires, token) is False
