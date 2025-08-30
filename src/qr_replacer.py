from __future__ import annotations
from typing import List
import numpy as np
from PIL import Image

# OpenCV is used for QR detection + perspective warps.
try:
    import cv2  # type: ignore
except Exception as e:  # pragma: no cover
    cv2 = None  # graceful fallback; we'll raise a clear error when needed
    print("Warning: OpenCV (cv2) is not installed. exit code 1.")
    exit(1)
# ---------- Internal helpers ----------

def _ensure_rgb(img: Image.Image) -> Image.Image:
    return img.convert("RGB") if img.mode != "RGB" else img

def _rgb_to_bgr_cv(img: Image.Image) -> np.ndarray:
    """Change PIL RGB tp OpenCV BGR uint8 array so open CV can use the photo."""
    a = np.array(img, dtype=np.uint8)
    if a.ndim == 2:
        a = np.stack([a, a, a], axis=-1)
    # RGB -> BGR

    return a[:, :, ::-1].copy()

def _order_qr_point_clockwise(pts: np.ndarray) -> np.ndarray:
    """Ensure 4 points are ordered [TL, TR, BR, BL].
    Accepts shape (4,2). Returns float32 array.
    """
    pts = np.asarray(pts, dtype=np.float32)
    if pts.shape != (4, 2):
        raise ValueError("quad must be shape (4,2)")
    # TL has smallest sum, BR has largest sum. TR has smallest diff, BL largest diff.
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(d)]
    bl = pts[np.argmax(d)]
    return np.array([tl, tr, br, bl], dtype=np.float32)

def _calculate_qr_area_sise(quad: np.ndarray) -> float:
    q = _order_qr_point_clockwise(quad)
    # polygon area (shoelace)
    x = q[:, 0]
    y = q[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

def _detect_qrs_in_image(image_rgb: Image.Image) -> List[np.ndarray]:
    """Return a list of detected QR quadrilaterals as (4,2) array.
    Uses OpenCV's QRCodeDetector. Returns an empty list if none.
    """
    qr_locations: List[np.ndarray] = []

    img_bgr = _rgb_to_bgr_cv(_ensure_rgb(image_rgb))
    
    detector = cv2.QRCodeDetector()
    result = detector.detectAndDecodeMulti(img_bgr)

    # Unpack depending on returned length
    if len(result) == 4:
        qr_detected, _ , qr_points_arr, _ = result
    elif len(result) == 3:
        qr_detected, _ , qr_points_arr = result
    else:
        raise RuntimeError(f"Unexpected return from detectAndDecodeMulti check OpenCV version. Got {len(result)} values.")

    if qr_detected and qr_points_arr is not None:
        for qr_points in qr_points_arr:
            if qr_points is None:
                continue
            try:
                qr_pos = _order_qr_point_clockwise(qr_points.reshape(4, 2))
                qr_locations.append(qr_pos)
            except ValueError:
                # skip invalid eight points
                continue

    if not qr_locations:
        # try to detect a single QR code
        qr_points = detector.detect(img_bgr)[1]  # returns (retval, points)
        if qr_points is not None:
            try:
                qr_pos = _order_qr_point_clockwise(qr_points.reshape(4, 2))
                qr_locations.append(qr_pos)
            except ValueError:
                # skip invalid eight points
                pass
            
    # Remove duplicates that are very close to each other
    qr_locations = _remove_duplicate_quads(qr_locations, tolerance=3.0)
    
    return qr_locations

def _remove_duplicate_quads(quads: List[np.ndarray], tolerance: float = 3.0) -> List[np.ndarray]:
    """
    Remove duplicate QR code detections that are very close to each other.

    Parameters
    ----------
    quads : List[np.ndarray]
        List of detected QR quadrilaterals (shape (4,2) arrays).
    tolerance : float, default 3.0
        Maximum difference in pixels to consider two quads as duplicates.

    Returns
    -------
    List[np.ndarray]
        List of unique quads with duplicates removed.
    """
    unique_quads: List[np.ndarray] = []

    for q in quads:
        if not any(np.allclose(q, uq, atol=tolerance) for uq in unique_quads):
            unique_quads.append(q)

    return unique_quads

def _make_qr_image_square(image: Image.Image) -> Image.Image:
    """Center-crop the QR image to square."""

    w, h = image.size
    if w == h:
        return image
    
    side = min(w, h)
    # center-crop to square
    left = (w - side) // 2
    top = (h - side) // 2

    return image.crop((left, top, left + side, top + side))

def _replace_qr_in_photo(background: Image.Image, new_qr: Image.Image, old_qr_loc: np.ndarray) -> Image.Image:
    """Replace the 'old_qr_loc' quadrilateral in 'background' with 'new_qr'.
    
    """
    new_qr = _ensure_rgb(new_qr)
    new_qr = _make_qr_image_square(new_qr)

    x_min = int(np.min(old_qr_loc[:, 0]))
    y_min = int(np.min(old_qr_loc[:, 1]))
    x_max = int(np.max(old_qr_loc[:, 0]))
    y_max = int(np.max(old_qr_loc[:, 1]))

    width = x_max - x_min
    height = y_max - y_min

    new_qr_resized = new_qr.resize((width, height))

    result = background.copy()
    result.paste(new_qr_resized, (x_min, y_min))

    return result


# ---------- Public API ----------
def replace_QR(original_image: Image.Image,
    new_qr_images: List[Image.Image],
    replace_all: bool = False,
    blend_edges: bool = True,
) -> Image.Image:
    """Detect QR codes in `original_image` and replace with `new_qr_image` by the size order
    Parameters:
    original_image - PIL.Image(RGB recommended).
        The image in which to detect and replace QR codes.
    new_qr_image - list of PIL.Image
        Every image have just the QR code image in it.
    replace_all - bool, default False
        If True, replace all detected codes. If False, replace the largest one only.

    Returns the original_image with the QR code(s) replaced.
    """
    if len(new_qr_images) == 0:
        raise ValueError("No new QR image(s) provided to insert.")
    
    new_qr_images = [_ensure_rgb(img) for img in new_qr_images]
    original_image = _ensure_rgb(original_image)
    qr_locations = _detect_qrs_in_image(original_image)

    if not qr_locations or len(qr_locations) == 0:
        raise RuntimeError("No QR code detected in the image.")
    if len(qr_locations) < len(new_qr_images):
        print(f"Warning: Detected {len(qr_locations)} QR code(s) but only {len(new_qr_images)} new QR image(s) provided. Some codes will not be replaced.")

    # Sort detected QR codes by area (largest first)
    qr_locations = sorted(qr_locations, key=_calculate_qr_area_sise, reverse=True)

    # If replace_all is False, only replace the largest QR
    if not replace_all:
        qr_locations = [qr_locations[0]]
        
    result = original_image.copy()

    for old_qr, new_qr in zip(qr_locations, new_qr_images):
        result = _replace_qr_in_photo(result, new_qr, old_qr)

    return result