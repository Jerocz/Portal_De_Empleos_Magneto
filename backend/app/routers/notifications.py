from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db
from app.security import get_current_user
# SOLID: Dependency Inversion - depende de la abstracción MatchRepository
from app.repositories.match_repository import MatchRepository

# SOLID: Single Responsibility - solo gestiona la lógica de notificaciones
router = APIRouter(prefix="/notifications", tags=["Notificaciones"])

# Umbral mínimo de score para considerar una notificación relevante
SCORE_MINIMO = 60


@router.get("/")
def get_notifications(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retorna los matches con score >= 60% como notificaciones relevantes."""
    # GRASP: Bajo Acoplamiento - no conoce SQL; delega al Repository
    match_repo = MatchRepository(db)
    rows = match_repo.find_notifications(current_user["id"], SCORE_MINIMO)

    notificaciones = [
        {
            "id": n["id"],
            "titulo": f"Match con {n['title']} en {n['company']}",
            "mensaje": n["explanation"],
            "score": float(n["score"]),
            "ciudad": n["city"],
            "modalidad": n["modality"],
            "fecha": str(n["run_date"]),
        }
        for n in rows
    ]

    return {"total": len(notificaciones), "notificaciones": notificaciones}
