from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.routers import auth, profile, jobs, matching, notifications, applications
from app.routers import ws as ws_router
from app.routers import messages

app = FastAPI(title="Portal de Empleos Magneto API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno del servidor: {str(exc)}"},
    )

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(notifications.router)
app.include_router(applications.router)
app.include_router(messages.router)
app.include_router(ws_router.router)   # WebSocket /ws/{user_id}

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
