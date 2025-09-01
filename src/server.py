import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import register_routes
from src.config import logger, set_logger_level
from src.config.settings import settings


log_level = "debug" # debug, info, warning, error  
set_logger_level(log_level)

# Print startup message
print(f"Starting server on {settings.server_host}:{settings.server_port}")
logger.info(f"Starting server on {settings.server_host}:{settings.server_port}")

app = FastAPI()
    
# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # or specific frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routers
register_routes(app)

# Simple endpoints
@app.get("/")
def index():
    return {"message": "Server is up"}

@app.get("/health")
def health_check():
    return {"status": "Server is running"}

if __name__ == "__main__":
    uvicorn.run(
        "src.server:app",             # import string required for reload
        host=settings.server_host,    # uses your settings
        port=settings.server_port,    # uses your settings
        reload=True,                  # development auto-reload
        log_level=log_level
    )