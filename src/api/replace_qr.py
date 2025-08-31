import requests
from io import BytesIO
from fastapi import APIRouter, HTTPException
from src.services import replace_qr_in_pdf_bytes  # our in-memory PDF function
from src.config import settings
from pydantic import BaseModel

router = APIRouter()

class ReplaceQRRequest(BaseModel):
    ticket_id: str

async def replace_qr_code(request_model: ReplaceQRRequest):
    """
    Endpoint to replace QR codes in a PDF associated with a ticket ID.
    """
    ticket_id = request_model.ticket_id
    if not ticket_id:
        raise HTTPException(status_code=400, detail="ticket_id is required")

    # Fetch PDF URL from Supabase using ticket ID
    result = settings.supabase.table("ticket_units").select("ticket_pdf_url").eq("id", ticket_id).execute()
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket_pdf_url = result.data[0]["ticket_pdf_url"]
    if not ticket_pdf_url:
        raise HTTPException(status_code=404, detail="No PDF URL found for the provided ticket ID")

    # Download PDF
    try:
        response = requests.get(ticket_pdf_url)
        response.raise_for_status()
        pdf_bytes = response.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot access the PDF: {str(e)}")

    # Replace QR codes in memory
    try:
        new_pdf_bytes = replace_qr_in_pdf_bytes(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR code replacement failed: {str(e)}")

    # Upload to Supabase storage
    bucket_name = "ticket-pdfs"
    storage_path = f"replaced/replaced_{ticket_id}.pdf"
    pdf_buffer = BytesIO(new_pdf_bytes)

    try:
        settings.supabase.storage.from_(bucket_name).upload(
            path=storage_path,
            file=pdf_buffer,
            file_options={"content-type": "application/pdf", "upsert": "true"}
        )
        public_url = settings.supabase.storage.from_(bucket_name).get_public_url(storage_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF to Supabase storage: {str(e)}")

    # Update DB with new PDF URL
    try:
        settings.supabase.table("ticket_units").update({
            "ticket_pdf_url": public_url
        }).eq("id", ticket_id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update DB with new PDF URL: {str(e)}")

    return {"message": "QR code replaced successfully", "new_pdf_url": public_url}
