# server.py:
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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
app.state.last_pdf_url = None

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

app.state.last_pdf_url = "#"

@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Simple HTML page showing server status and last PDF.
    """
    last_pdf_url = app.state.last_pdf_url

    html_content = f"""
    <html>
        <head><title>QR-Replacer Server</title></head>
        <body>
            <h1>QR-Replacer Server</h1>
            <p>Status: <strong>UP </strong></p>
            <p>Last converted PDF: <a href="{last_pdf_url}">Download PDF</a></p>
        </body>
    </html>
    """
    return HTMLResponse(html_content)

@app.get("/health")
async def health_check():
    return {"status": "Server is running with new code"}

@app.get("/")
async def root():
    return {"status": "ok", "message": "QR Replacer API running"}

####################################################
