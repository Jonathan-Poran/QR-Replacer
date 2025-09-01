import fitz  # PyMuPDF
from pathlib import Path
from src.services.pdf_QR_replacer import replace_qr_in_pdf_bytes


def replace_qr_in_pdf(input_pdf_path: str, output_dir: str = "output_pdfs", output_name: str = None):
    """
    Replace QR codes in a local PDF using replace_qr_in_pdf_bytes,
    then save the modified PDF to disk.
    """
    input_pdf = Path(input_pdf_path)
    if not input_pdf.exists():
        raise FileNotFoundError(f"PDF not found: {input_pdf}")

    # Read the input PDF as bytes
    with open(input_pdf, "rb") as f:
        pdf_bytes = f.read()

    # Replace QR codes (in memory)
    replaced_bytes = replace_qr_in_pdf_bytes(pdf_bytes)

    # Prepare output path
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if output_name:
        output_path = output_dir / output_name
    else:
        output_path = output_dir / f"replaced_{input_pdf.stem}.pdf"

    # Save the replaced PDF
    with open(output_path, "wb") as f:
        f.write(replaced_bytes)

    print(f"QR code replaced successfully.\nNew PDF saved at: {output_path}")
    return output_path


if __name__ == "__main__":
    # Example usage
    input_pdf_path = "/Users/jonathanporan/Downloads/PrintAtHome-615810282275291.pdf"
    output_dir = "/Users/jonathanporan/Downloads/"

    replace_qr_in_pdf(input_pdf_path, output_dir)
