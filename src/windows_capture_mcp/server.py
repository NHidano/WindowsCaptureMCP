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
    encode_preview,
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


@mcp.tool()
def preview_window(hwnd: int) -> list[ImageContent]:
    """Capture a window and return a low-quality JPEG preview image.

    Useful for quickly checking window content before taking a full capture.

    Args:
        hwnd: Window handle to capture.

    Returns:
        MCP image content with a low-quality JPEG preview.
    """
    img = capture_window_image(hwnd)
    b64, mime_type = encode_preview(img)
    return [ImageContent(type="image", data=b64, mimeType=mime_type)]


@mcp.tool()
def preview_fullscreen(display_number: int = 1) -> list[ImageContent]:
    """Capture the full screen and return a low-quality JPEG preview image.

    Useful for quickly checking screen content before taking a full capture.

    Args:
        display_number: 1-based display number. Default is 1.

    Returns:
        MCP image content with a low-quality JPEG preview.
    """
    img = capture_fullscreen_image(display_number)
    b64, mime_type = encode_preview(img)
    return [ImageContent(type="image", data=b64, mimeType=mime_type)]


@mcp.tool()
def preview_region(
    x: int,
    y: int,
    width: int,
    height: int,
    display_number: int = 1,
) -> list[ImageContent]:
    """Capture a specific region and return a low-quality JPEG preview image.

    Useful for quickly checking a region before taking a full capture.

    Args:
        x: Left coordinate relative to the display.
        y: Top coordinate relative to the display.
        width: Width in pixels.
        height: Height in pixels.
        display_number: 1-based display number. Default is 1.

    Returns:
        MCP image content with a low-quality JPEG preview.
    """
    img = capture_region_image(x, y, width, height, display_number)
    b64, mime_type = encode_preview(img)
    return [ImageContent(type="image", data=b64, mimeType=mime_type)]


@mcp.tool()
def focus_window(hwnd: int) -> str:
    """Bring a window to the foreground.

    Args:
        hwnd: Window handle.

    Returns:
        Text message with the operation result.
    """
    result = window.focus_window(hwnd)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def maximize_window(hwnd: int) -> str:
    """Maximize a window.

    Args:
        hwnd: Window handle.

    Returns:
        Text message with the operation result.
    """
    result = window.maximize_window(hwnd)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def resize_window(hwnd: int, width: int, height: int) -> str:
    """Resize a window while keeping its position.

    Args:
        hwnd: Window handle.
        width: New width in pixels.
        height: New height in pixels.

    Returns:
        Text message with the operation result.
    """
    result = window.resize_window(hwnd, width, height)
    return json.dumps(result, ensure_ascii=False)


@mcp.tool()
def move_window(hwnd: int, x: int, y: int) -> str:
    """Move a window while keeping its size.

    Args:
        hwnd: Window handle.
        x: New x position in pixels.
        y: New y position in pixels.

    Returns:
        Text message with the operation result.
    """
    result = window.move_window(hwnd, x, y)
    return json.dumps(result, ensure_ascii=False)


def main():
    mcp.run(transport="stdio")
