from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.deps import get_db
from app.security import get_current_user
# SOLID: Dependency Inversion - depende de abstracciones (Repository y Factory)
from app.repositories.profile_repository import ProfileRepository
from app.factories.dto_factory import DTOFactory

# SOLID: Single Responsibility - este router solo gestiona el perfil del usuario
router = APIRouter(prefix="/profile", tags=["Perfil"])


class ProfileUpdate(BaseModel):
    location_city: Optional[str] = None
    modality: Optional[str] = None  # remote, hybrid, on-site
    salary_min_cop: Optional[int] = None
    salary_max_cop: Optional[int] = None
    years_exp: Optional[int] = None
    skills: Optional[List[str]] = None


@router.get("/")
def get_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # GRASP: Controlador - delega lectura al Repository y construcción de respuesta al Factory
    profile_repo = ProfileRepository(db)
    profile = profile_repo.find_by_user_id(current_user["id"])
    # GRASP: Fabricación Pura - DTOFactory construye el objeto de respuesta
    dto = DTOFactory.create_user_profile_dto(current_user, profile)
    return DTOFactory.user_profile_dto_to_dict(dto)


@router.put("/")
def update_profile(
    data: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile_repo = ProfileRepository(db)
    profile_repo.upsert(
        user_id=current_user["id"],
        location_city=data.location_city,
        modality=data.modality,
        salary_min_cop=data.salary_min_cop,
        salary_max_cop=data.salary_max_cop,
        years_exp=data.years_exp,
        skills=data.skills or [],
    )
    return {"message": "Perfil actualizado correctamente"}
