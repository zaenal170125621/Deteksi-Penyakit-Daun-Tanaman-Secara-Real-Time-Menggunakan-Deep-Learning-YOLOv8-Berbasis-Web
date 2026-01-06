"""
Utility functions for image processing and file operations.
"""
import base64
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Tuple


def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Decode image bytes to BGR numpy array.

    Args:
        image_bytes: Raw image bytes (JPEG, PNG, etc.)

    Returns:
        BGR numpy array

    Raises:
        ValueError: If image cannot be decoded
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Failed to decode image")
        return img
    except Exception as e:
        raise ValueError(f"Error decoding image: {str(e)}")


def encode_image_to_jpeg(image_bgr: np.ndarray, quality: int = 85) -> bytes:
    """
    Encode BGR image to JPEG bytes.

    Args:
        image_bgr: BGR numpy array
        quality: JPEG quality (0-100)

    Returns:
        JPEG bytes
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode('.jpg', image_bgr, encode_param)
    return buffer.tobytes()


def image_to_base64_jpeg(image_bgr: np.ndarray, quality: int = 85) -> str:
    """
    Convert BGR image to base64-encoded JPEG string.

    Args:
        image_bgr: BGR numpy array
        quality: JPEG quality (0-100)

    Returns:
        Base64-encoded JPEG string
    """
    jpeg_bytes = encode_image_to_jpeg(image_bgr, quality)
    return base64.b64encode(jpeg_bytes).decode('utf-8')


def compute_brightness(image_bgr: np.ndarray) -> float:
    """
    Compute average brightness of image.

    Args:
        image_bgr: BGR numpy array

    Returns:
        Mean brightness value (0-255)
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray))


def compute_blur_metric(image_bgr: np.ndarray) -> float:
    """
    Compute blur metric using Laplacian variance.
    Higher values indicate sharper images.

    Args:
        image_bgr: BGR numpy array

    Returns:
        Laplacian variance (higher = sharper)
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return float(laplacian.var())


def compute_image_quality_metrics(image_bgr: np.ndarray) -> dict:
    """
    Compute comprehensive image quality metrics.

    Args:
        image_bgr: BGR numpy array

    Returns:
        Dictionary with quality metrics
    """
    return {
        'brightness': compute_brightness(image_bgr),
        'blur_metric': compute_blur_metric(image_bgr),
        'height': image_bgr.shape[0],
        'width': image_bgr.shape[1]
    }


def generate_timestamp_filename(prefix: str = "", extension: str = "") -> str:
    """
    Generate filename with timestamp.

    Args:
        prefix: Optional prefix
        extension: File extension (with or without dot)

    Returns:
        Filename string like "capture_20231228_143052_123456.jpg"
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    if prefix:
        filename = f"{prefix}_{timestamp}"
    else:
        filename = timestamp

    if extension:
        if not extension.startswith('.'):
            extension = f".{extension}"
        filename += extension

    return filename


def compute_bbox_area_ratio(bbox_xyxy: list, image_width: int, image_height: int) -> float:
    """
    Compute ratio of bounding box area to image area.

    Args:
        bbox_xyxy: [x1, y1, x2, y2]
        image_width: Image width
        image_height: Image height

    Returns:
        Area ratio (0-1)
    """
    x1, y1, x2, y2 = bbox_xyxy
    bbox_area = (x2 - x1) * (y2 - y1)
    image_area = image_width * image_height
    return bbox_area / image_area if image_area > 0 else 0.0


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists, create if needed.

    Args:
        path: Directory path

    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path
