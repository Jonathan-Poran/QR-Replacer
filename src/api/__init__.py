# src/api/__init__.py
from fastapi import FastAPI
from .replace_qr import router as replace_qr_router

def register_routes(app: FastAPI):
    app.include_router(replace_qr_router)