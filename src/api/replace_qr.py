from PIL import Image
from fastapi import APIRouter, HTTPException
from src.services import replace_QR
from src.config import settings
from pathlib import Path
from pydantic import BaseModel

router = APIRouter()

class ReplaceQRRequest(BaseModel):
    ticket_id: str
    
async def replace_qr_code(request_model: ReplaceQRRequest):
    """
    Endpoint to replace QR codes in an image associated with a ticket ID.
    """
    ticket_id = request_model["ticket_id"]
    if not ticket_id:
        raise HTTPException(status_code=400, detail="ticket_id is required")

    # Fetch the image URL from Supabase using the ticket ID 
    data = settings.supabase.table("ticket_units").select("ticket_image").eq("id", ticket_id).execute()
    if not data.data or len(data.data) == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    image = data.data[0]["ticket_image"]
    if not image:
        raise HTTPException(status_code=404, detail="No image found for the provided ticket ID")
    

    base_path = Path(__file__).parent
    new_qr_image_path = base_path / "swapit_qr_code.png"
    new_ticket_image = replace_QR(image, [], replace_all=False)
    new_qr_image = Image.open(new_qr_image_path).convert("RGB")

    new_ticket_image = replace_QR(image, [new_qr_image], replace_all=False)

    # Save the modified image locally (or to a temporary location)
    output_path = base_path / f"replaced_{ticket_id}.png"
    new_ticket_image.save(output_path)

    response = settings.supabase.table("ticket_units").update({
        "ticket_image": new_ticket_image
    }).eq("id", ticket_id).execute() 
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to update the ticket image in the database")
    
    return {"message": "QR code replaced successfully", "new_image_path": str(output_path)}

