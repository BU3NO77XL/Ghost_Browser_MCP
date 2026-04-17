"""Tests for server startup configuration parsing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_minimal_disables_non_core_sections():
    import server

    disabled = server._disabled_sections_from_args(["server.py", "--minimal"])

    assert "element-extraction" in disabled
    assert "network-debugging" in disabled
    assert "cdp-functions" in disabled
    assert "fetch-management" in disabled
    assert "target-management" in disabled
    assert "browser-management" not in disabled
    assert "element-interaction" not in disabled


def test_explicit_disable_flags_map_to_sections():
    import server

    disabled = server._disabled_sections_from_args(
        [
            "server.py",
            "--disable-browser-management",
            "--disable-cdp-functions",
            "--disable-fetch-management",
            "--disable-target-management",
            "--transport",
            "http",
        ]
    )

    assert disabled == {
        "browser-management",
        "cdp-functions",
        "fetch-management",
        "target-management",
    }


def test_all_tool_sections_have_disable_flags():
    import server

    assert set(server._DISABLE_FLAG_TO_SECTION.values()) == set(server._TOOL_SECTIONS)
