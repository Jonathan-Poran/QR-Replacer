import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Settings():
    # Server
    server_host: str = os.getenv("SERVER_HOST", "127.0.0.1")
    server_port: int = int(os.getenv("SERVER_PORT", 3000))
    server_url: str = os.getenv("SERVER_URL", "http://localhost")
    
    # Logger
    log_level: str = "DEBUG"
    
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)




settings = Settings()