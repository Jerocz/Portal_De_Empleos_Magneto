from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.deps import get_db
from app.security import get_current_user
from app.matching.service import MatchingService
from app.repositories.match_repository import MatchRepository
from app.repositories.profile_repository import ProfileRepository
from app.factories.dto_factory import DTOFactory

router = APIRouter(prefix="/matches", tags=["Matching"])


@router.post("/run")
def run_matching(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Recalcula el ranking de empleos para el usuario.
    Guarda todos los empleos con puntaje: 25 pts por cada campo que coincide
    (ciudad, modalidad, salario, skills). Máximo 100 pts = 4 campos.
    """
    profile_repo = ProfileRepository(db)
    profile = profile_repo.find_by_user_id(current_user["id"]) or {}

    service = MatchingService(db)
    resultado = service.run_matching(current_user["id"], profile)

    total = resultado["total"]
    afinidad = resultado["con_afinidad"]
    return {
        "message": f"Se analizaron {total} empleos. {afinidad} tienen afinidad contigo."
    }


@router.get("/")
def get_my_matches(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retorna todos los empleos rankeados por puntaje de afinidad (mayor a menor)."""
    match_repo = MatchRepository(db)
    matches = match_repo.find_by_user(current_user["id"], limit=200)
    return [DTOFactory.match_dto_to_dict(DTOFactory.create_match_result_dto(m)) for m in matches]
