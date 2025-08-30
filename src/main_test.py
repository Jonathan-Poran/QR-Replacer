from pathlib import Path
from PIL import Image
from QR_replacer import replace_QR

def main():

    # --- Paths ---
    original_image_path = Path("TestImages/NadavEvent.png")
    new_qr_image_path = Path("TestImages/largeQRcode.png")
    output_image_path = Path("TestImages/ReplacedQR.png")
    
    # --- Load images ---
    original_image = Image.open(original_image_path).convert("RGB")
    new_qr_image = Image.open(new_qr_image_path).convert("RGB")

    # --- Replace QR code ---
    result_image = replace_QR(original_image, [new_qr_image], replace_all=False)

    # --- Save result ---
    result_image.save(output_image_path)
    print(f"Saved QR-replaced image to {output_image_path}")

if __name__ == "__main__":
    main()
