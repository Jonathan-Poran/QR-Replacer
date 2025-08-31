import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from pathlib import Path
from src.services import replace_QR

def replace_qr_in_pdf(input_pdf_path: str, qr_image_path: str, output_dir: str = "output_pdfs", output_name: str = None):
    """
    Replace QR codes in a local PDF with a custom QR image and save a new PDF.
    Uses PyMuPDF (fitz) instead of pdf2image + Poppler.
    """
    input_pdf = Path(input_pdf_path)
    if not input_pdf.exists():
        raise FileNotFoundError(f"PDF not found: {input_pdf}")

    qr_image_file = Path(qr_image_path)
    if not qr_image_file.exists():
        raise FileNotFoundError(f"QR image not found: {qr_image_file}")

    # Load QR image
    swapit_QR = Image.open(qr_image_file).convert("RGB")

    # Open PDF with PyMuPDF
    doc = fitz.open(input_pdf)

    # Store modified pages as PIL images
    modified_images = []
    i = 1
    for page in doc:
        # Render page as PNG image
        zoom = 3  # 3x scaling
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Replace QR codes on this page
        new_img = replace_QR(img, [swapit_QR], replace_all=True,num_page=i)
        modified_images.append(new_img)
        i = i+1

    if not modified_images:
        raise RuntimeError("QR code replacement failed")

    # Save output PDF
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_name:
        output_path = output_dir / output_name
    else:
        output_path = output_dir / f"replaced_{input_pdf.stem}.pdf"

    # Convert PIL images back to PDF
    modified_images[0].save(
        output_path,
        save_all=True,
        append_images=modified_images[1:],
        format="PDF"
    )

    print(f"QR code replaced successfully.\nNew PDF saved at: {output_path}")
    return output_path


if __name__ == "__main__":
    # Example usage
    input_pdf_path = "/Users/jonathanporan/Downloads/PrintAtHome-615810282275291.pdf"
    qr_image_path = "/Users/jonathanporan/Documents/GitHub/MTA/Third Year/QR-Replacer/TestImages/swapit_qr_code.png"
    output_dir = "/Users/jonathanporan/Downloads/"

    replace_qr_in_pdf(input_pdf_path, qr_image_path, output_dir)
