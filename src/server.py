import uvicorn
from src.config import app #FastAPI instance; required by Uvicorn
from src.config import settings, logger, set_logger_level

log_level = "debug" # debug, info, warning, error  
set_logger_level(log_level)

# Print startup message
print(f"Starting server on {settings.server_host}:{settings.server_port}")
logger.info(f"Starting server on {settings.server_host}:{settings.server_port}")

if __name__ == "__main__":
    uvicorn.run(
        "src.server:app",             # import string required for reload
        host=settings.server_host,    # uses your settings
        port=settings.server_port,    # uses your settings
        reload=True,                  # development auto-reload
        log_level=log_level
    )