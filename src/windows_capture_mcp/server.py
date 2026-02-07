"""MCP server for Windows screen capture."""

import json

from mcp.server.fastmcp import FastMCP

from windows_capture_mcp import display, window

mcp = FastMCP("windows-capture-mcp")


@mcp.tool()
def list_windows(filter: str | None = None, include_hidden: bool = False) -> str:
    """List visible windows with optional filtering.

    Args:
        filter: Optional title substring filter (case-insensitive).
        include_hidden: If True, include invisible windows. Default is False.

    Returns:
        JSON string with list of window information.
    """
    results = window.list_windows(filter=filter, include_hidden=include_hidden)
    return json.dumps(results, ensure_ascii=False)


@mcp.tool()
def list_displays() -> str:
    """List all connected displays with their information.

    Returns:
        JSON string with list of display information.
    """
    results = display.get_displays()
    return json.dumps(results, ensure_ascii=False)


def main():
    mcp.run(transport="stdio")
