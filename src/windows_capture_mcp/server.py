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

_VALID_FORMATS = ("png", "jpeg", "webp")


def _validate_format(format: str) -> None:
    """Raise ValueError if the image format is not supported."""
    if format.lower() not in _VALID_FORMATS:
        raise ValueError(
            f"Unsupported format: {format!r}. Must be one of: {', '.join(_VALID_FORMATS)}"
        )


def _validate_quality(quality: int) -> None:
    """Raise ValueError if quality is out of range."""
    if not (1 <= quality <= 100):
        raise ValueError(f"Quality must be between 1 and 100, got {quality}")


def _validate_size(width: int, height: int) -> None:
    """Raise ValueError if width or height is not positive."""
    if width <= 0 or height <= 0:
        raise ValueError(
            f"Width and height must be positive, got {width}x{height}"
        )


def _validate_display_number(display_number: int) -> None:
    """Raise ValueError if display_number is not positive."""
    if display_number < 1:
        raise ValueError(
            f"Display number must be >= 1, got {display_number}"
        )


@mcp.tool()
def list_windows(filter: str | None = None, include_hidden: bool = False) -> str:
    """List visible windows with optional filtering.

    Args:
        filter: Optional title substring filter (case-insensitive).
        include_hidden: If True, include invisible windows. Default is False.

    Returns:
        JSON string with list of window information.
    """
    try:
        results = window.list_windows(filter=filter, include_hidden=include_hidden)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Failed to list windows: {e}") from e


@mcp.tool()
def list_displays() -> str:
    """List all connected displays with their information.

    Returns:
        JSON string with list of display information.
    """
    try:
        results = display.get_displays()
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Failed to list displays: {e}") from e


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
    _validate_format(format)
    _validate_quality(quality)
    try:
        img = capture_window_image(hwnd)
        b64, mime_type = encode_image(img, format=format, quality=quality)
        return [ImageContent(type="image", data=b64, mimeType=mime_type)]
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to capture window (hwnd={hwnd}): {e}") from e


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
    _validate_display_number(display_number)
    _validate_format(format)
    _validate_quality(quality)
    try:
        img = capture_fullscreen_image(display_number)
        b64, mime_type = encode_image(img, format=format, quality=quality)
        return [ImageContent(type="image", data=b64, mimeType=mime_type)]
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(
            f"Failed to capture fullscreen (display={display_number}): {e}"
        ) from e


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
    _validate_size(width, height)
    _validate_display_number(display_number)
    _validate_format(format)
    _validate_quality(quality)
    try:
        img = capture_region_image(x, y, width, height, display_number)
        b64, mime_type = encode_image(img, format=format, quality=quality)
        return [ImageContent(type="image", data=b64, mimeType=mime_type)]
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(
            f"Failed to capture region ({x}, {y}, {width}x{height}): {e}"
        ) from e


@mcp.tool()
def preview_window(hwnd: int) -> list[ImageContent]:
    """Capture a window and return a low-quality JPEG preview image.

    Useful for quickly checking window content before taking a full capture.

    Args:
        hwnd: Window handle to capture.

    Returns:
        MCP image content with a low-quality JPEG preview.
    """
    try:
        img = capture_window_image(hwnd)
        b64, mime_type = encode_preview(img)
        return [ImageContent(type="image", data=b64, mimeType=mime_type)]
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to preview window (hwnd={hwnd}): {e}") from e


@mcp.tool()
def preview_fullscreen(display_number: int = 1) -> list[ImageContent]:
    """Capture the full screen and return a low-quality JPEG preview image.

    Useful for quickly checking screen content before taking a full capture.

    Args:
        display_number: 1-based display number. Default is 1.

    Returns:
        MCP image content with a low-quality JPEG preview.
    """
    _validate_display_number(display_number)
    try:
        img = capture_fullscreen_image(display_number)
        b64, mime_type = encode_preview(img)
        return [ImageContent(type="image", data=b64, mimeType=mime_type)]
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(
            f"Failed to preview fullscreen (display={display_number}): {e}"
        ) from e


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
    _validate_size(width, height)
    _validate_display_number(display_number)
    try:
        img = capture_region_image(x, y, width, height, display_number)
        b64, mime_type = encode_preview(img)
        return [ImageContent(type="image", data=b64, mimeType=mime_type)]
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(
            f"Failed to preview region ({x}, {y}, {width}x{height}): {e}"
        ) from e


@mcp.tool()
def focus_window(hwnd: int) -> str:
    """Bring a window to the foreground.

    Args:
        hwnd: Window handle.

    Returns:
        Text message with the operation result.
    """
    try:
        result = window.focus_window(hwnd)
        return json.dumps(result, ensure_ascii=False)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to focus window (hwnd={hwnd}): {e}") from e


@mcp.tool()
def maximize_window(hwnd: int) -> str:
    """Maximize a window.

    Args:
        hwnd: Window handle.

    Returns:
        Text message with the operation result.
    """
    try:
        result = window.maximize_window(hwnd)
        return json.dumps(result, ensure_ascii=False)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to maximize window (hwnd={hwnd}): {e}") from e


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
    _validate_size(width, height)
    try:
        result = window.resize_window(hwnd, width, height)
        return json.dumps(result, ensure_ascii=False)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to resize window (hwnd={hwnd}): {e}") from e


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
    try:
        result = window.move_window(hwnd, x, y)
        return json.dumps(result, ensure_ascii=False)
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to move window (hwnd={hwnd}): {e}") from e


def main():
    mcp.run(transport="stdio")
