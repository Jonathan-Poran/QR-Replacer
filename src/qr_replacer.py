from PIL import Image
import numpy as np
import qrcode
from utils.geometry import Quadrilateral


def generate_qr_image(data, box_size=10, border=0):
    """
    Generate a QR code image from the given data.
    """
    qr = qrcode.QRCode(
        version=None,
        box_size=box_size,
        border=border
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    return img


def warp_qr_to_quad(background: Image.Image, qr_img: Image.Image, quad: Quadrilateral):
    """
    Warp the QR image to fit the quadrilateral on the background image.
    Returns a new PIL Image with the QR replaced.
    """
    # Source coordinates (QR corners)
    w, h = qr_img.size
    src = np.array([[0, 0],
                    [w, 0],
                    [w, h],
                    [0, h]], dtype=np.float32)

    # Destination coordinates (Quadrilateral points)
    dst = np.array([
        [quad.p1.x, quad.p1.y],
        [quad.p2.x, quad.p2.y],
        [quad.p3.x, quad.p3.y],
        [quad.p4.x, quad.p4.y]
    ], dtype=np.float32)

    # Compute perspective transform matrix
    matrix = Image.transform._quad_transform(src, dst)

    # Apply transform
    qr_warped = qr_img.transform(background.size, Image.PERSPECTIVE, matrix, Image.BICUBIC)

    # Paste with alpha mask to preserve transparency
    background.paste(qr_warped, (0, 0), qr_warped)
    return background


def replace_qr(image_path: str, qr_data: str, detected_quads):
    """
    Load image, generate QR, warp and replace QR codes at detected quadrilaterals.
    detected_quads: list of Quadrilateral objects
    Returns modified PIL Image.
    """
    image = Image.open(image_path).convert("RGBA")
    qr_img = generate_qr_image(qr_data)

    for quad in detected_quads:
        image = warp_qr_to_quad(image, qr_img, quad)

    return image
