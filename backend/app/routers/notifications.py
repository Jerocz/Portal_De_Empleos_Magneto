from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from app.deps import get_db
from app.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notificaciones"])

SCORE_MINIMO = 60  # Solo notifica matches con score >= 60%


@router.get("/")
def get_notifications(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retorna los matches con score alto como notificaciones.
    Un match con score >= 60% se considera una notificacion relevante.
    """
    rows = db.execute(
        text("""
            SELECT jm.id, jm.score, jm.explanation, jm.run_date, jm.created_at,
                   j.title, j.company, j.city, j.modality
            FROM job_matches jm
            JOIN jobs j ON j.id = jm.job_id
            WHERE jm.user_id = :uid AND jm.score >= :min_score
            ORDER BY jm.created_at DESC
            LIMIT 10
        """),
        {"uid": current_user["id"], "min_score": SCORE_MINIMO}
    ).fetchall()

    notificaciones = []
    for row in rows:
        n = dict(row._mapping)
        notificaciones.append({
            "id": n["id"],
            "titulo": f"Match con {n['title']} en {n['company']}",
            "mensaje": n["explanation"],
            "score": float(n["score"]),
            "ciudad": n["city"],
            "modalidad": n["modality"],
            "fecha": str(n["run_date"]),
        })

    return {
        "total": len(notificaciones),
        "notificaciones": notificaciones
    }
