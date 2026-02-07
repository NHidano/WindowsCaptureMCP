"""Screen capture logic."""

import base64
import ctypes
import ctypes.wintypes
import io

import win32gui
import win32ui
import win32con
from PIL import Image

from windows_capture_mcp.display import get_display_rect


def capture_rect(x: int, y: int, width: int, height: int) -> Image.Image:
    """Capture a rectangle from the screen and return as a Pillow Image.

    Args:
        x: Left coordinate in virtual desktop pixels.
        y: Top coordinate in virtual desktop pixels.
        width: Width in pixels.
        height: Height in pixels.

    Returns:
        A Pillow Image of the captured region.
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"width and height must be positive, got {width}x{height}")

    # Get a device context for the entire virtual screen
    hdesktop = win32gui.GetDesktopWindow()
    desktop_dc = win32gui.GetWindowDC(hdesktop)
    src_dc = win32ui.CreateDCFromHandle(desktop_dc)
    mem_dc = src_dc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(src_dc, width, height)
    mem_dc.SelectObject(bmp)

    # BitBlt from the screen
    mem_dc.BitBlt((0, 0), (width, height), src_dc, (x, y), win32con.SRCCOPY)

    # Convert to Pillow Image
    bmp_info = bmp.GetInfo()
    bmp_bits = bmp.GetBitmapBits(True)
    img = Image.frombuffer(
        "RGB",
        (bmp_info["bmWidth"], bmp_info["bmHeight"]),
        bmp_bits,
        "raw",
        "BGRX",
        0,
        1,
    )

    # Clean up GDI resources
    mem_dc.DeleteDC()
    src_dc.DeleteDC()
    win32gui.ReleaseDC(hdesktop, desktop_dc)
    win32gui.DeleteObject(bmp.GetHandle())

    return img


def capture_window_image(hwnd: int) -> Image.Image:
    """Capture a window by its handle and return as a Pillow Image.

    Args:
        hwnd: Window handle.

    Returns:
        A Pillow Image of the captured window.

    Raises:
        ValueError: If the hwnd is invalid.
    """
    if not win32gui.IsWindow(hwnd):
        raise ValueError(f"Invalid window handle: {hwnd}")

    rect = win32gui.GetWindowRect(hwnd)
    x, y, right, bottom = rect
    width = right - x
    height = bottom - y

    if width <= 0 or height <= 0:
        raise ValueError(f"Window has no visible area: {width}x{height}")

    return capture_rect(x, y, width, height)


def capture_fullscreen_image(display_number: int = 1) -> Image.Image:
    """Capture the full screen of a specified display.

    Args:
        display_number: 1-based display number (default: 1).

    Returns:
        A Pillow Image of the full display.
    """
    x, y, width, height = get_display_rect(display_number)
    return capture_rect(x, y, width, height)


def capture_region_image(
    x: int, y: int, width: int, height: int, display_number: int = 1
) -> Image.Image:
    """Capture a specific region relative to a display.

    The x/y coordinates are relative to the specified display's top-left corner.
    They are converted to absolute virtual desktop coordinates before capture.

    Args:
        x: Left coordinate relative to the display.
        y: Top coordinate relative to the display.
        width: Width in pixels.
        height: Height in pixels.
        display_number: 1-based display number (default: 1).

    Returns:
        A Pillow Image of the captured region.
    """
    disp_x, disp_y, _disp_w, _disp_h = get_display_rect(display_number)
    abs_x = disp_x + x
    abs_y = disp_y + y
    return capture_rect(abs_x, abs_y, width, height)


_FORMAT_MIME = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}


def encode_image(
    image: Image.Image, format: str = "png", quality: int = 90
) -> tuple[str, str]:
    """Encode a Pillow Image to a base64 string.

    Args:
        image: The Pillow Image to encode.
        format: Image format – "png", "jpeg", or "webp".
        quality: Compression quality (1-100). Used for jpeg and webp.

    Returns:
        A tuple of (base64_string, mime_type).

    Raises:
        ValueError: If the format is not supported.
    """
    fmt = format.lower()
    if fmt not in _FORMAT_MIME:
        raise ValueError(
            f"Unsupported format: {format!r}. Use one of: {', '.join(_FORMAT_MIME)}"
        )

    mime_type = _FORMAT_MIME[fmt]

    buf = io.BytesIO()
    save_kwargs: dict = {"format": fmt.upper() if fmt != "jpeg" else "JPEG"}
    if fmt in ("jpeg", "webp"):
        save_kwargs["quality"] = quality

    # JPEG does not support RGBA; convert if necessary
    img = image
    if fmt == "jpeg" and image.mode in ("RGBA", "LA", "P"):
        img = image.convert("RGB")

    img.save(buf, **save_kwargs)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return b64, mime_type
