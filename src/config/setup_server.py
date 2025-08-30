from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import register_routes

def setup_server() -> FastAPI:
    """
    Create and configure FastAPI app with routes, middleware, and background tasks.
    """
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

    return app

app = setup_server()