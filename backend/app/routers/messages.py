from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.deps import get_db
from app.security import get_current_user
from app.repositories.message_repository import MessageRepository
from app.repositories.application_repository import ApplicationRepository
from app.websocket_manager import manager

router = APIRouter(prefix="/messages", tags=["Mensajes"])


class SendMessage(BaseModel):
    application_id: int
    content: str


@router.post("/send")
async def send_message(
    data: SendMessage,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Solo empleadores pueden enviar mensajes")
    if not data.content.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

    app_repo = ApplicationRepository(db)
    postulacion = app_repo.find_by_id_for_employer(data.application_id, current_user["id"])
    if not postulacion:
        raise HTTPException(status_code=404, detail="Postulación no encontrada o no te pertenece")

    msg_repo = MessageRepository(db)
    msg = msg_repo.create(
        application_id=data.application_id,
        sender_id=current_user["id"],
        receiver_id=postulacion["employee_id"],
        content=data.content.strip(),
    )

    if not msg:
        raise HTTPException(status_code=500, detail="Error al guardar el mensaje")

    # Notificación WebSocket instantánea al empleado
    await manager.send_to(postulacion["employee_id"], {
        "tipo":            "mensaje_empleador",
        "application_id":  data.application_id,
        "vacante":         postulacion["job_title"],
        "empresa":         postulacion["company"],
        "remitente":       current_user["full_name"],
        "mensaje":         data.content.strip(),
    })

    return {"message": "Mensaje enviado", "id": msg["id"]}


@router.get("/unread")
def get_unread(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") != "employee":
        raise HTTPException(status_code=403, detail="Solo empleados pueden ver sus mensajes")
    repo = MessageRepository(db)
    return repo.find_unread_by_receiver(current_user["id"])


@router.get("/history/{application_id}")
def get_history(
    application_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = MessageRepository(db)
    return repo.find_by_application(application_id)


@router.post("/read/{application_id}")
def mark_read(
    application_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = MessageRepository(db)
    repo.mark_read(application_id, current_user["id"])
    return {"message": "Mensajes marcados como leídos"}
