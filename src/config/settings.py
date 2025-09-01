import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

class Settings:
    def __init__(self):
        # Server
        self.server_host = os.getenv("SERVER_HOST", "127.0.0.1")
        self.server_port = int(os.getenv("SERVER_PORT", 3000))
        self.server_url = os.getenv("SERVER_URL", "http://localhost")
        
        # Logger
        self.log_level = "DEBUG"
        
        # Supabase
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)


settings = Settings()
