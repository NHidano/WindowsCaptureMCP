"""MCP server for Windows screen capture."""

import json

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent

from windows_capture_mcp import DEFAULT_FORMAT, DEFAULT_QUALITY, display, window
from windows_capture_mcp.capture import (
    capture_fullscreen_image,
    capture_region_image,
    capture_window_image,
    encode_image,
)

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


@mcp.tool()
def capture_window(
    hwnd: int,
    format: str = DEFAULT_FORMAT,
    quality: int = DEFAULT_QUALITY,
) -> list[ImageContent]:
    """Capture a window by its handle and return as an image.

    Args:
        hwnd: Window handle to capture.
        format: Image format – "png", "jpeg", or "webp". Default is "png".
        quality: JPEG/WebP compression quality (1-100). Default is 90.

    Returns:
        MCP image content with the captured window.
    """
    img = capture_window_image(hwnd)
    b64, mime_type = encode_image(img, format=format, quality=quality)
    return [ImageContent(type="image", data=b64, mimeType=mime_type)]


@mcp.tool()
def capture_fullscreen(
    display_number: int = 1,
    format: str = DEFAULT_FORMAT,
    quality: int = DEFAULT_QUALITY,
) -> list[ImageContent]:
    """Capture the full screen of a specified display.

    Args:
        display_number: 1-based display number. Default is 1.
        format: Image format – "png", "jpeg", or "webp". Default is "png".
        quality: JPEG/WebP compression quality (1-100). Default is 90.

    Returns:
        MCP image content with the captured fullscreen.
    """
    img = capture_fullscreen_image(display_number)
    b64, mime_type = encode_image(img, format=format, quality=quality)
    return [ImageContent(type="image", data=b64, mimeType=mime_type)]


@mcp.tool()
def capture_region(
    x: int,
    y: int,
    width: int,
    height: int,
    display_number: int = 1,
    format: str = DEFAULT_FORMAT,
    quality: int = DEFAULT_QUALITY,
) -> list[ImageContent]:
    """Capture a specific region relative to a display.

    Args:
        x: Left coordinate relative to the display.
        y: Top coordinate relative to the display.
        width: Width in pixels.
        height: Height in pixels.
        display_number: 1-based display number. Default is 1.
        format: Image format – "png", "jpeg", or "webp". Default is "png".
        quality: JPEG/WebP compression quality (1-100). Default is 90.

    Returns:
        MCP image content with the captured region.
    """
    img = capture_region_image(x, y, width, height, display_number)
    b64, mime_type = encode_image(img, format=format, quality=quality)
    return [ImageContent(type="image", data=b64, mimeType=mime_type)]


def main():
    mcp.run(transport="stdio")
