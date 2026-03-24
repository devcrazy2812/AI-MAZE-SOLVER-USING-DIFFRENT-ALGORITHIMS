"""
Safe image upload validation and processing.

Validates file type, size, and dimensions before converting
the uploaded image into a binary numpy grid for maze solving.
"""

import numpy as np
from PIL import Image
from pathlib import Path
import io
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import MAX_UPLOAD_SIZE_MB, SUPPORTED_IMAGE_FORMATS


class InvalidImageError(Exception):
    """Raised when the uploaded image fails validation."""
    pass


class ImageTooLargeError(InvalidImageError):
    """Raised when the image exceeds the maximum allowed size."""
    pass


def validate_upload(uploaded_file) -> bool:
    """
    Validate an uploaded file (Streamlit UploadedFile or file-like object).

    Args:
        uploaded_file: The uploaded file object.

    Returns:
        True if valid.

    Raises:
        InvalidImageError: If the file type is unsupported.
        ImageTooLargeError: If the file is too large.
    """
    if uploaded_file is None:
        raise InvalidImageError("No file uploaded.")

    # Check file name / extension
    filename = getattr(uploaded_file, "name", "")
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_IMAGE_FORMATS:
        raise InvalidImageError(
            f"Unsupported file format '{ext}'. "
            f"Supported: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
        )

    # Check file size
    size_bytes = getattr(uploaded_file, "size", None)
    if size_bytes is None:
        # Fallback: read to check length
        data = uploaded_file.read()
        uploaded_file.seek(0)
        size_bytes = len(data)

    max_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise ImageTooLargeError(
            f"File size ({size_bytes / 1024 / 1024:.1f} MB) exceeds "
            f"maximum ({MAX_UPLOAD_SIZE_MB} MB)."
        )

    return True


def process_image(uploaded_file) -> np.ndarray:
    """
    Process an uploaded image into a binary numpy grid.

    Args:
        uploaded_file: File-like object or Streamlit UploadedFile.

    Returns:
        np.ndarray of shape (rows, cols) with values 0 (wall) or 1 (path).

    Raises:
        InvalidImageError: If the image cannot be processed.
    """
    validate_upload(uploaded_file)

    try:
        im = Image.open(uploaded_file).convert("L")
    except Exception as e:
        raise InvalidImageError(f"Cannot read image: {e}")

    width, height = im.size
    if width < 3 or height < 3:
        raise InvalidImageError(
            f"Image too small ({width}x{height}). Minimum 3x3 required."
        )

    if width > 1000 or height > 1000:
        raise InvalidImageError(
            f"Image too large ({width}x{height}). Maximum 1000x1000."
        )

    data = np.array(im)
    grid = (data > 128).astype(np.uint8)

    return grid
