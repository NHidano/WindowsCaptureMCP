"""Screen capture logic."""

import ctypes
import ctypes.wintypes

import win32gui
import win32ui
import win32con
from PIL import Image


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
