"""Helpers for reading MCP client roots without exposing Context in tool schemas."""

from typing import Any, List

from core.output_paths import file_uri_to_path


async def get_client_root_paths(ctx: Any = None) -> List[str]:
    """Return client root paths advertised by the MCP client, if available."""
    if ctx is None:
        return []
    try:
        roots = await ctx.list_roots()
    except Exception:
        return []
    return [file_uri_to_path(str(getattr(root, "uri", ""))) for root in roots]
