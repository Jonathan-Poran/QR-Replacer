from pathlib import Path
from PIL import Image
from QRreplacesor import replace_QR

def main():
    # --- Paths ---
    original_image_path = Path("../TestImages/basicQRcode.png")
    new_qr_image_path = Path("../TestImages/newQRcode.png")
    output_image_path = Path("../TestImages/output.png")

    # --- Load images ---
    original_image = Image.open(original_image_path).convert("RGB")
    new_qr_image = Image.open(new_qr_image_path).convert("RGB")

    # --- Replace QR code ---
    result_image = replace_QR(original_image, new_qr_image)

    # --- Save result ---
    result_image.save(output_image_path)
    print(f"Saved QR-replaced image to {output_image_path}")

if __name__ == "__main__":
    main()
