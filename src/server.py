import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from mangum import Mangum
from pathlib import Path

# Import your modules
from src.api import register_routes
from src.config import logger, set_logger_level
from src.config.settings import settings

# --- Logger ---
log_level = "debug"  # debug, info, warning, error
set_logger_level(log_level)
logger.info(f"Starting server (serverless)")

# --- FastAPI app ---
app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # or specific frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Register routes ---
register_routes(app)

# --- Minimal frontend ---
LAST_PDF_URL = os.getenv("LAST_PDF_URL", "#")  # use Supabase link in production

@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Simple HTML page showing server status and last PDF.
    """
    html_content = f"""
    <html>
        <head><title>QR-Replacer Server</title></head>
        <body>
            <h1>QR-Replacer Server</h1>
            <p>Status: <strong>UP ✅</strong></p>
            <p>Last converted PDF: <a href="{LAST_PDF_URL}">Download PDF</a></p>
        </body>
    </html>
    """
    return HTMLResponse(html_content)

@app.get("/health")
async def health_check():
    return {"status": "Server is running"}

# --- Wrap app for Vercel serverless ---
handler = Mangum(app)
