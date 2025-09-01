import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from src.services import replace_QR
from pathlib import Path

SWAPIT_QR_PATH = Path(__file__).parent.parent / "assets" / "SWAPIT_QR.png"
# Fixed QR image path (always the same QR)

def replace_qr_in_pdf_bytes(pdf_bytes: bytes) -> bytes:
    """
    Replace QR codes in a PDF (in memory) and return a new PDF as bytes.
    Uses a fixed QR image defined in FIXED_QR_PATH.
    """
    # Load fixed QR image
    swapit_QR = Image.open(SWAPIT_QR_PATH).convert("RGB")
    swapit_QR = swapit_QR.resize((1000, 1000), Image.LANCZOS)

    # Open PDF from bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    modified_images = []

    page_num = 1
    for page in doc:
        original_width = int(page.rect.width)
        original_height = int(page.rect.height)

        # Render page to high-res image
        zoom = 3.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Replace QR codes (5% bigger, centered)
        new_img = replace_QR(img, [swapit_QR], replace_all=True, page_num=page_num)
        
        new_img_resized = new_img.resize((original_width, original_height), Image.LANCZOS)

        modified_images.append(new_img_resized)
        page_num +=1

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
