from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.deps import get_db
from app.security import get_current_user
# SOLID: Dependency Inversion - depende de abstracciones (Service, Repository, Factory)
from app.matching.service import MatchingService
from app.repositories.match_repository import MatchRepository
from app.repositories.profile_repository import ProfileRepository
from app.factories.dto_factory import DTOFactory

# SOLID: Single Responsibility - este router solo expone los endpoints de matching
# GRASP: Controlador - recibe requests HTTP y delega toda la lógica a MatchingService
router = APIRouter(prefix="/matches", tags=["Matching"])


@router.post("/run")
def run_matching(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Ejecuta el algoritmo de matching ponderado (Skills 60%, Salario 25%, Modalidad 15%)
    y guarda los resultados en base de datos.
    """
    profile_repo = ProfileRepository(db)
    profile = profile_repo.find_by_user_id(current_user["id"])

    if not profile or not profile.get("skills"):
        raise HTTPException(status_code=400, detail="Completa tu perfil con tus skills primero")

    # GRASP: Indirección - MatchingService actúa como intermediario entre el router y las Strategies
    service = MatchingService(db)
    nuevos_matches = service.run_matching(current_user["id"], profile)

    return {"message": f"Matching completado. {nuevos_matches} nuevos matches encontrados hoy."}


@router.get("/")
def get_my_matches(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retorna los mejores matches del usuario, ordenados por score ponderado."""
    # GRASP: Bajo Acoplamiento - el router no conoce SQL; solo llama al Repository
    match_repo = MatchRepository(db)
    matches = match_repo.find_by_user(current_user["id"])
    return [DTOFactory.match_dto_to_dict(DTOFactory.create_match_result_dto(m)) for m in matches]
