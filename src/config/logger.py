import logging
import os
from logging.handlers import RotatingFileHandler

# Make a logs folder if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Logger setup
logger = logging.getLogger("app_logger")
logger.propagate = True
#logger.setLevel(logging.INFO)  - @@uvicorn controls it

def set_logger_level(level_str: str):
    level = getattr(logging, level_str.upper(), logging.INFO)
    logger.setLevel(level)
    for h in logger.handlers:
        h.setLevel(level)
        
# Formatter with timestamp
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler (rotates when file reaches 5 MB, keeps 3 backups)
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
