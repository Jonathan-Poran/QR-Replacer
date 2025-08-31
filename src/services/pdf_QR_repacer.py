import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from src.services import replace_QR
from pathlib import Path

# Fixed QR image path (always the same QR)
FIXED_QR_PATH = Path("/Users/jonathanporan/Documents/GitHub/MTA/Third Year/QR-Replacer/TestImages/swapit_qr_code.png")

def replace_qr_in_pdf_bytes(pdf_bytes: bytes) -> bytes:
    """
    Replace QR codes in a PDF (in memory) and return a new PDF as bytes.
    Uses a fixed QR image defined in FIXED_QR_PATH.
    """
    # Load fixed QR image
    swapit_QR = Image.open(FIXED_QR_PATH).convert("RGB")

    # Open PDF from bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    modified_images = []

    zoom = 3.0  # fixed high-res rendering
    for page in doc:
        # Render page to high-res image
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Replace QR codes (5% bigger, centered)
        new_img = replace_QR(img, [swapit_QR], replace_all=True)
        modified_images.append(new_img)

    if not modified_images:
        raise RuntimeError("QR code replacement failed")

    # Save modified images to in-memory PDF
    out_pdf = BytesIO()
    modified_images[0].save(
        out_pdf,
        format="PDF",
        save_all=True,
        append_images=modified_images[1:]
    )
    out_pdf.seek(0)
    return out_pdf.read()
