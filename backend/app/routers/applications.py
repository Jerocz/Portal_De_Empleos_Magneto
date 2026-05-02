from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.deps import get_db
from app.security import get_current_user
from app.repositories.application_repository import ApplicationRepository
from app.websocket_manager import manager

router = APIRouter(prefix="/applications", tags=["Postulaciones"])

# Mensajes legibles por estado
STATUS_LABELS = {
    "seen":     "👀 El empleador vio tu postulación",
    "rejected": "✗ Tu postulación fue rechazada",
    "pending":  "⏳ Tu postulación volvió a estado pendiente",
}


class ApplyData(BaseModel):
    job_id: int
    message: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str  # seen | rejected | pending


@router.post("/")
async def apply_to_job(
    data: ApplyData,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") != "employee":
        raise HTTPException(status_code=403, detail="Solo empleados pueden postularse")

    repo = ApplicationRepository(db)
    if repo.already_applied(data.job_id, current_user["id"]):
        raise HTTPException(status_code=400, detail="Ya te postulaste a esta vacante")

    app = repo.create(data.job_id, current_user["id"], data.message)

    # ── Notificar al empleador en tiempo real ──
    info = repo.find_job_employer(data.job_id, db)
    if info:
        await manager.send_to(info["employer_id"], {
            "tipo":       "nueva_postulacion",
            "vacante":    info["job_title"],
            "candidato":  current_user["full_name"],
            "mensaje":    f"{current_user['full_name']} se postuló a '{info['job_title']}'",
        })

    return {"message": "Postulación enviada correctamente", "application_id": app["id"]}


@router.get("/my-applications")
def my_applications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") != "employee":
        raise HTTPException(status_code=403, detail="Solo empleados pueden ver sus postulaciones")
    repo = ApplicationRepository(db)
    return repo.find_by_employee(current_user["id"])


@router.get("/inbox")
def employer_inbox(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Solo contratantes pueden ver postulaciones")
    repo = ApplicationRepository(db)
    return repo.find_by_employer(current_user["id"])


@router.patch("/{application_id}/status")
async def update_status(
    application_id: int,
    data: StatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Solo contratantes pueden actualizar el estado")
    if data.status not in ("seen", "rejected", "pending"):
        raise HTTPException(status_code=400, detail="Estado inválido")

    repo = ApplicationRepository(db)
    result = repo.update_status_with_employee(application_id, current_user["id"], data.status)

    if not result:
        raise HTTPException(status_code=404, detail="Postulación no encontrada")

    # ── Notificación WebSocket en tiempo real ──
    employee_id  = result["employee_id"]
    job_title    = result["job_title"]
    label        = STATUS_LABELS.get(data.status, data.status)

    await manager.send_to(employee_id, {
        "tipo":        "estado_postulacion",
        "application_id": application_id,
        "vacante":     job_title,
        "estado":      data.status,
        "mensaje":     f"{label} para '{job_title}'",
    })

    return {"message": "Estado actualizado"}


@router.delete("/{application_id}")
def withdraw_application(
    application_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") != "employee":
        raise HTTPException(status_code=403, detail="Solo empleados pueden retirar postulaciones")
    repo = ApplicationRepository(db)
    deleted = repo.delete(application_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Postulación no encontrada")
    return {"message": "Postulación retirada"}
