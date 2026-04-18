"""System info management MCP tools for querying browser/GPU/process information via CDP."""

import os
import platform
import sys
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List

from fastmcp import Context

from core.client_roots import get_client_root_paths
from core.login_guard import check_pending_login_guard
from core.output_paths import file_uri_to_path, get_client_workspace, get_host_root, get_host_root_mount
from core.platform_utils import is_running_in_container
from core.system_info_handler import SystemInfoHandler


def _is_host_path_absolute(path: str) -> bool:
    return Path(path).is_absolute() or PureWindowsPath(path).is_absolute()


def register(mcp, section_tool, deps):
    browser_manager = deps["browser_manager"]

    @section_tool("system-info-management")
    async def get_server_info(ctx: Context = None) -> Dict[str, Any]:
        """
        Return information about the MCP server process itself.

        Use this to discover the server's working directory and OS so you can
        build correct absolute output_path values when calling file-extraction
        or save_page_html tools.

        Returns:
            Dict with:
                cwd         — current working directory of the server process
                platform    — operating system name (Windows / Linux / Darwin)
                python      — Python version string
                path_sep    — path separator for this OS (\\ on Windows, / elsewhere)
                home        — user home directory
        """
        info = {
            "cwd": str(Path.cwd().absolute()),
            "platform": platform.system(),
            "python": sys.version.split()[0],
            "path_sep": os.sep,
            "home": str(Path.home()),
        }
        if is_running_in_container():
            host_hint = os.environ.get("GHOST_CLIENT_WORKSPACE_HOST", "ghost_browser_mcp_output")
            info["container"] = True
            info["client_workspace_mount"] = str(get_client_workspace())
            info["client_workspace_host_hint"] = host_hint
            info["client_workspace_host_hint_is_absolute"] = _is_host_path_absolute(host_hint)
            info["host_root"] = get_host_root()
            info["host_root_mount"] = str(get_host_root_mount())
            info["output_path_guidance"] = (
                "In Docker mode, save artifacts under /workspace or pass normal paths like "
                "/app/name/file.html; they will be redirected to the client-visible "
                "workspace mount. Files in this mounted workspace are user-facing outputs "
                "and are not automatically deleted by the server cleanup sweep."
            )
            if not _is_host_path_absolute(host_hint):
                info["docker_workspace_note"] = (
                    "client_path_hint is relative to the host folder mounted as /workspace. "
                    "If your agent is working in another local directory, restart Docker with "
                    "GHOST_HOST_WORKSPACE and GHOST_CLIENT_WORKSPACE_HOST pointing at that "
                    "directory."
                )
        else:
            info["container"] = False
        if ctx is not None:
            try:
                root_paths = await get_client_root_paths(ctx)
                info["client_roots"] = [
                    {
                        "path": file_uri_to_path(str(path)),
                    }
                    for path in root_paths
                ]
            except Exception as e:
                info["client_roots_error"] = str(e)
        return info

    @section_tool("system-info-management")
    async def system_info_get_info(instance_id: str) -> Dict[str, Any]:
        """
        Return information about the system for a browser instance.

        Queries the CDP SystemInfo domain to retrieve GPU information, model
        name, and command line used to launch the browser.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            Dict with keys ``gpu``, ``model_name``, and ``command_line``.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SystemInfoHandler.get_info(tab)

    @section_tool("system-info-management")
    async def system_info_get_feature_state(instance_id: str, feature_flag: str) -> Dict[str, bool]:
        """
        Return the state of a browser feature flag for a browser instance.

        Queries the CDP SystemInfo domain to check whether a specific browser
        feature flag is enabled.

        Args:
            instance_id (str): Browser instance ID.
            feature_flag (str): The name of the feature flag to query.

        Returns:
            Dict with key ``feature_enabled`` (bool).
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SystemInfoHandler.get_feature_state(tab, feature_flag)

    @section_tool("system-info-management")
    async def system_info_get_process_info(
        instance_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Return information about all running browser processes for a browser instance.

        Queries the CDP SystemInfo domain to retrieve a list of all running
        browser processes with their IDs, types, and CPU times.

        Args:
            instance_id (str): Browser instance ID.

        Returns:
            List of dicts each with ``id``, ``type``, and ``cpu_time`` keys.
        """
        guard = await check_pending_login_guard(instance_id)
        if guard:
            return guard
        tab = await browser_manager.get_tab(instance_id)
        if not tab:
            raise Exception(f"Instance not found: {instance_id}")
        return await SystemInfoHandler.get_process_info(tab)

    return {k: v for k, v in locals().items() if callable(v) and not k.startswith("_")}
