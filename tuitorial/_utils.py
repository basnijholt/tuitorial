import os
import secrets
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from typing import Final
from urllib.parse import urlparse

import httpx
from PIL import Image

DEFAULT_ALLOWED_CONTENT_TYPES = ("image/jpeg", "image/png", "image/gif", "image/webp")
DEFAULT_ALLOWED_FILE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")
FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "GIF": "image/gif",
    "WEBP": "image/webp",
}

EXTENSION_TO_FORMAT = {
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".png": "png",
    ".gif": "gif",
    ".webp": "webp",
}


class ImageValidationError(ValueError):
    """Raised when image validation fails."""


@contextmanager
def _temp_file() -> Iterator[tempfile._TemporaryFileWrapper]:
    """Create a temporary file that's always cleaned up."""
    tmp_file = tempfile.NamedTemporaryFile(prefix=secrets.token_hex(8), delete=False)  # noqa: SIM115
    try:
        yield tmp_file
    finally:
        tmp_file.close()
        with suppress(OSError):
            os.unlink(tmp_file.name)  # noqa: PTH108


@dataclass
class ImageDownloadConfig:
    MAX_FILE_SIZE: Final[int] = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_DIMENSION: Final[int] = 4096  # pixels
    MIN_IMAGE_DIMENSION: Final[int] = 1  # pixels
    TIMEOUT: Final[int] = 10  # seconds
    MAX_REDIRECTS: Final[int] = 5
    ALLOWED_CONTENT_TYPES: Final[tuple[str, ...]] = DEFAULT_ALLOWED_CONTENT_TYPES
    ALLOWED_FILE_EXTENSIONS: Final[tuple[str, ...]] = DEFAULT_ALLOWED_FILE_EXTENSIONS


def _validate_url(url: str, allowed_extensions: tuple[str, ...]) -> tuple[str, str]:
    """Validate URL format and extension.

    Returns
    -------
    tuple[str, str]
        The validated URL and file extension

    """
    try:
        parsed = urlparse(url)
        if not all(
            [
                parsed.scheme in ("http", "https"),
                parsed.netloc,
                any(parsed.path.lower().endswith(ext) for ext in allowed_extensions),
            ],
        ):
            msg = f"Invalid or unsafe URL: {url}"
            raise ValueError(msg)  # noqa: TRY301
        return url, os.path.splitext(parsed.path)[1].lower()  # noqa: PTH122
    except Exception as e:
        msg = f"Invalid URL format: {e}"
        raise ValueError(msg) from e


def _validate_image(
    img: Image.Image,
    file_ext: str,
    config: ImageDownloadConfig,
) -> None:
    """Validate image dimensions and format."""
    if (
        img.width > config.MAX_IMAGE_DIMENSION
        or img.height > config.MAX_IMAGE_DIMENSION
        or img.width < config.MIN_IMAGE_DIMENSION
        or img.height < config.MIN_IMAGE_DIMENSION
    ):
        msg = f"Invalid image dimensions: {img.width}x{img.height}"
        raise ImageValidationError(msg)

    actual_format = img.format.lower() if img.format else None
    expected_format = EXTENSION_TO_FORMAT.get(file_ext)
    if not actual_format or actual_format != expected_format:
        msg = f"Image format mismatch: got {actual_format}, expected {expected_format}"
        raise ImageValidationError(msg)


def _validate_response_headers(response: httpx.Response, config: ImageDownloadConfig) -> None:
    """Validate content length and type from response headers."""
    content_length = response.headers.get("content-length")
    if content_length and int(content_length) > config.MAX_FILE_SIZE:
        msg = f"File too large (from headers): {content_length} bytes"
        raise ValueError(msg)

    content_type = response.headers.get("content-type", "").lower()
    if content_type not in config.ALLOWED_CONTENT_TYPES:
        msg = f"Invalid content type: {content_type}"
        raise ValueError(msg)


def _stream_to_file(
    response: httpx.Response,
    tmp_file: tempfile._TemporaryFileWrapper,
    max_size: int,
) -> None:
    """Stream response content to file while checking size."""
    size = 0
    for chunk in response.iter_bytes():
        size += len(chunk)
        if size > max_size:
            msg = f"File too large: {size} bytes"
            raise ValueError(msg)
        tmp_file.write(chunk)
    tmp_file.flush()


def _verify_image_format(img: Image.Image, config: ImageDownloadConfig) -> None:
    """Verify the image format is valid and allowed."""
    if not img.format:
        msg = "Unable to determine image format"
        raise ValueError(msg)

    format_to_mime = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "GIF": "image/gif",
        "WEBP": "image/webp",
    }

    detected_mime = format_to_mime.get(img.format)
    if not detected_mime or detected_mime not in config.ALLOWED_CONTENT_TYPES:
        msg = f"Invalid image format: {img.format}"
        raise ValueError(msg)


def _download_to_tempfile(url: str, config: ImageDownloadConfig) -> tuple[str, Image.Image]:
    """Download image to temporary file and perform initial validations."""
    with (
        _temp_file() as tmp_file,
        httpx.Client(
            timeout=config.TIMEOUT,
            follow_redirects=True,
            max_redirects=config.MAX_REDIRECTS,
        ) as client,
        client.stream("GET", url) as response,
    ):
        response.raise_for_status()
        _validate_response_headers(response, config)
        _stream_to_file(response, tmp_file, config.MAX_FILE_SIZE)

        try:
            img = Image.open(tmp_file.name)
        except Exception as e:
            msg = f"Failed to open image: {e}"
            raise ImageValidationError(msg) from e

        _verify_image_format(img, config)
        return tmp_file.name, img


def download_image(url: str, config: ImageDownloadConfig | None = None) -> Image.Image:
    """Securely download and validate an image from a URL.

    Parameters
    ----------
    url
        The URL to download the image from
    config
        Optional configuration for download limits and validation

    Returns
    -------
    Image
        The downloaded and validated PIL Image

    Raises
    ------
    ValueError
        If the image is invalid or unsafe
    httpx.HTTPError
        If the download fails

    """
    if config is None:
        config = ImageDownloadConfig()

    url, file_ext = _validate_url(url, config.ALLOWED_FILE_EXTENSIONS)

    tmp_path = None
    try:
        tmp_path, img = _download_to_tempfile(url, config)
        img.load()  # Force load the image to catch any malformed data
        _validate_image(img, file_ext, config)
        return img
    finally:
        if tmp_path:
            with suppress(OSError):
                os.unlink(tmp_path)  # noqa: PTH108
