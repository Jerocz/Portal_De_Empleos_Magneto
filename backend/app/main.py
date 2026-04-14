from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import auth, profile, jobs, matching, notifications

app = FastAPI(title="Portal de Empleos Magneto API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(notifications.router)

# Servir el frontend (montado al final para no interferir con rutas de la API)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
