"""Image processing and validation service for TimeLens.

Handles in-memory validation, EXIF orientation normalization,
aspect-ratio preserving resizing, and JPEG format conversion.
"""

import io
import hashlib
from typing import Dict, Any, Tuple, Optional
from PIL import Image, ImageOps

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_FORMATS = {"JPEG", "JPG", "PNG"}
MAX_DIMENSION = 1280

# Guard against decompression bomb attacks while allowing standard photos
Image.MAX_IMAGE_PIXELS = 50_000_000


def compute_image_hash(data: bytes) -> str:
    """Compute SHA-256 hash of raw byte data."""
    return hashlib.sha256(data).hexdigest()


def validate_and_process_uploaded_image(
    uploaded_file: Any,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Validate and process an uploaded file object or bytes.

    Args:
        uploaded_file: Streamlit UploadedFile or file-like object with .read()/.getvalue() or bytes.

    Returns:
        (image_data_dict, error_message)
        image_data_dict contains:
            - 'original_format': str
            - 'original_size': Tuple[int, int] (width, height)
            - 'processed_size': Tuple[int, int] (width, height)
            - 'jpeg_bytes': bytes
            - 'hash': str (sha256)
            - 'pil_image': PIL.Image.Image (for display)
    """
    if uploaded_file is None:
        return None, "No file provided."

    # Extract raw bytes
    try:
        if isinstance(uploaded_file, bytes):
            raw_bytes = uploaded_file
        elif hasattr(uploaded_file, "getvalue"):
            raw_bytes = uploaded_file.getvalue()
        elif hasattr(uploaded_file, "read"):
            raw_bytes = uploaded_file.read()
        else:
            return None, "Invalid file object type."
    except Exception as e:
        return None, f"Could not read uploaded file: {str(e)}"

    # Check file size
    if len(raw_bytes) == 0:
        return None, "The uploaded file is empty."
    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        mb = len(raw_bytes) / (1024 * 1024)
        return None, f"File size ({mb:.2f} MB) exceeds maximum allowed limit of 10 MB."

    # Validate image decoding with Pillow
    try:
        raw_stream = io.BytesIO(raw_bytes)
        with Image.open(raw_stream) as img:
            fmt = (img.format or "").upper()
            if fmt == "JPG":
                fmt = "JPEG"
            if fmt not in ALLOWED_FORMATS:
                return (
                    None,
                    f"Unsupported format '{fmt}'. Please upload a JPG, JPEG, or PNG image.",
                )

            orig_size = img.size
            if orig_size[0] <= 0 or orig_size[1] <= 0:
                return None, "Image has invalid dimensions."

            # Normalize orientation using EXIF data
            transposed = ImageOps.exif_transpose(img)

            # Ensure RGB mode (handles RGBA, Palette, Grayscale)
            if transposed.mode != "RGB":
                rgb_img = transposed.convert("RGB")
            else:
                rgb_img = transposed.copy()

            # Resize maintaining aspect ratio if oversized
            if max(rgb_img.size) > MAX_DIMENSION:
                rgb_img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)

            processed_size = rgb_img.size

            # Encode to JPEG bytes in-memory
            output_buf = io.BytesIO()
            rgb_img.save(output_buf, format="JPEG", quality=85, optimize=True)
            jpeg_bytes = output_buf.getvalue()

            content_hash = compute_image_hash(jpeg_bytes)

            return {
                "original_format": fmt,
                "original_size": orig_size,
                "processed_size": processed_size,
                "jpeg_bytes": jpeg_bytes,
                "hash": content_hash,
                "pil_image": rgb_img,
            }, None

    except Image.DecompressionBombError:
        return None, "Image exceeds maximum safe resolution limits."
    except Exception as e:
        return None, f"Failed to decode image: {type(e).__name__} - {str(e)}"

