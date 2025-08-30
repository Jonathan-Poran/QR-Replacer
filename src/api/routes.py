from fastapi import FastAPI
from . import replace_qr

def register_routes(app: FastAPI):
    app.include_router(replace_qr.router, prefix="/replace-qr", tags=["QR Replacement"])
    

