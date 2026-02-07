"""Tests for the capture module."""

import base64
import io

import pytest
from PIL import Image

from windows_capture_mcp.capture import (
    capture_rect,
    encode_image,
    encode_preview,
)


class TestCaptureRect:
    """Tests for capture_rect."""

    def test_capture_rect_returns_image(self):
        """capture_rect returns a Pillow Image for a small screen area."""
        img = capture_rect(0, 0, 100, 100)
        assert isinstance(img, Image.Image)
        assert img.size == (100, 100)

    def test_capture_rect_different_size(self):
        """capture_rect respects the requested width and height."""
        img = capture_rect(0, 0, 200, 150)
        assert img.size == (200, 150)

    def test_capture_rect_invalid_size(self):
        """capture_rect raises ValueError for non-positive dimensions."""
        with pytest.raises(ValueError):
            capture_rect(0, 0, 0, 100)
        with pytest.raises(ValueError):
            capture_rect(0, 0, 100, -1)


class TestEncodeImage:
    """Tests for encode_image."""

    @pytest.fixture()
    def sample_image(self):
        """Create a simple test image."""
        return Image.new("RGB", (320, 240), color=(255, 0, 0))

    def test_encode_png(self, sample_image):
        """encode_image produces valid PNG base64."""
        b64, mime = encode_image(sample_image, format="png")
        assert mime == "image/png"
        data = base64.b64decode(b64)
        img = Image.open(io.BytesIO(data))
        assert img.format == "PNG"
        assert img.size == (320, 240)

    def test_encode_jpeg(self, sample_image):
        """encode_image produces valid JPEG base64."""
        b64, mime = encode_image(sample_image, format="jpeg", quality=80)
        assert mime == "image/jpeg"
        data = base64.b64decode(b64)
        img = Image.open(io.BytesIO(data))
        assert img.format == "JPEG"
        assert img.size == (320, 240)

    def test_encode_webp(self, sample_image):
        """encode_image produces valid WebP base64."""
        b64, mime = encode_image(sample_image, format="webp", quality=80)
        assert mime == "image/webp"
        data = base64.b64decode(b64)
        img = Image.open(io.BytesIO(data))
        assert img.format == "WEBP"
        assert img.size == (320, 240)

    def test_encode_unsupported_format(self, sample_image):
        """encode_image raises ValueError for unsupported formats."""
        with pytest.raises(ValueError):
            encode_image(sample_image, format="bmp")

    def test_encode_jpeg_converts_rgba(self):
        """encode_image converts RGBA images to RGB for JPEG."""
        rgba_img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        b64, mime = encode_image(rgba_img, format="jpeg")
        assert mime == "image/jpeg"
        data = base64.b64decode(b64)
        img = Image.open(io.BytesIO(data))
        assert img.mode == "RGB"


class TestEncodePreview:
    """Tests for encode_preview."""

    def test_preview_small_image_no_resize(self):
        """encode_preview does not resize images already within the limit."""
        img = Image.new("RGB", (640, 480))
        b64, mime = encode_preview(img)
        assert mime == "image/jpeg"
        data = base64.b64decode(b64)
        result = Image.open(io.BytesIO(data))
        assert result.size == (640, 480)

    def test_preview_large_image_resized(self):
        """encode_preview resizes large images so long side <= 1280."""
        img = Image.new("RGB", (3840, 2160))
        b64, mime = encode_preview(img)
        assert mime == "image/jpeg"
        data = base64.b64decode(b64)
        result = Image.open(io.BytesIO(data))
        long_side = max(result.size)
        assert long_side <= 1280

    def test_preview_tall_image_resized(self):
        """encode_preview handles portrait images correctly."""
        img = Image.new("RGB", (1080, 2400))
        b64, mime = encode_preview(img)
        assert mime == "image/jpeg"
        data = base64.b64decode(b64)
        result = Image.open(io.BytesIO(data))
        assert max(result.size) <= 1280
        # Aspect ratio should be approximately maintained
        assert result.size[0] < result.size[1]

    def test_preview_aspect_ratio_preserved(self):
        """encode_preview preserves the aspect ratio when resizing."""
        img = Image.new("RGB", (2560, 1440))
        b64, _ = encode_preview(img)
        data = base64.b64decode(b64)
        result = Image.open(io.BytesIO(data))
        original_ratio = 2560 / 1440
        result_ratio = result.size[0] / result.size[1]
        assert abs(original_ratio - result_ratio) < 0.02
