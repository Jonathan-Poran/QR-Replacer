# src/api/replace_qr.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os, requests
from io import BytesIO
from src.services.pdf_QR_replacer import replace_qr_in_pdf_bytes
from src.config.logger import logger
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

class ReplaceQRRequest(BaseModel):
    ticket_id: str

@router.post("/replace_qr")
async def replace_qr_code(request: Request,request_model: ReplaceQRRequest):
    """
    Endpoint to replace QR codes in a PDF associated with a ticket ID.
    """
    logger.info("Replace QR route triggered")
    ticket_id = request_model.ticket_id
    if not ticket_id:
        logger.warning("Bad request body")
        raise HTTPException(status_code=400, detail="ticket_id is required")

    # Fetch PDF URL from Supabase using ticket ID
    result = supabase.table("ticket_units").select("ticket_pdf_url").eq("id", ticket_id).execute()
    if not result.data or len(result.data) == 0:
        logger.warning("Ticket not found in Supabase")
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket_pdf_url = result.data[0]["ticket_pdf_url"]
    if not ticket_pdf_url:
        logger.warning("No PDF URL found in Supabase ticket")
        raise HTTPException(status_code=404, detail="No PDF URL found for the provided ticket ID")

    # Download PDF
    try:
        response = requests.get(ticket_pdf_url)
        response.raise_for_status()
        pdf_bytes = response.content
    except Exception as e:
        logger.error("No PDF URL found in Supabase ticket")
        raise HTTPException(status_code=500, detail=f"Cannot access the PDF: {str(e)}")

    # Replace QR codes in memory
    try:
        new_pdf_bytes = replace_qr_in_pdf_bytes(pdf_bytes)
    except Exception as e:
        logger.error(f"QR code replacement function failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"QR code replacement failed: {str(e)}")

    # Upload to Supabase storage
    bucket_name = "ticket-pdfs"
    storage_path = f"replaced/replaced_{ticket_id}.pdf"

    try:
        supabase.storage.from_(bucket_name).upload(
            path=storage_path,
            file=new_pdf_bytes,
            file_options={"content-type": "application/pdf", "upsert": "true"}
        )
        public_url = supabase.storage.from_(bucket_name).get_public_url(storage_path)
    
    except Exception as e:
        logger.warning(f"Failed to upload PDF to Supabase storage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload PDF to Supabase storage: {str(e)}")

    # Update DB with new PDF URL
    try:
        supabase.table("ticket_units").update({
            "ticket_pdf_url": public_url,
            "original_pdf_url": ticket_pdf_url
        }).eq("id", ticket_id).execute()
    except Exception as e:
        logger.warning(f"Failed to update DB with new PDF URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update DB with new PDF URL: {str(e)}")
    
    logger.info(f"QR code replaced successfully, new_pdf_url: {public_url}")
    request.app.state.last_pdf_url = public_url
    return {"message": "QR code replaced successfully", "new_pdf_url": public_url}
    