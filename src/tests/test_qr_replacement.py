from pathlib import Path
from PIL import Image
from src.services import replace_QR

def main():
    # --- Paths ---
    original_image_path = Path("TestImages/current/ticket.png")
    new_qr_image_path = Path("TestImages/current/swapit_qr_code.png")
    output_image_path = Path("TestImages/current/new_ticket.png")
    
    # --- Load images ---
    original_image = Image.open(original_image_path).convert("RGB")
    new_qr_image = Image.open(new_qr_image_path).convert("RGB")

    # --- Replace QR code ---
    result_image = replace_QR(original_image, [new_qr_image], replace_all=False, page_num= 1)

    # --- Save result ---
    result_image.save(output_image_path)
    print(f"Saved QR-replaced image to {output_image_path}")

if __name__ == "__main__":
    main()
