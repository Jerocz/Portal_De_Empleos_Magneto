from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.deps import get_db
from app.security import get_current_user
# SOLID: Dependency Inversion - depende de abstracciones (Repository y Factory)
from app.repositories.job_repository import JobRepository
from app.factories.dto_factory import DTOFactory

# SOLID: Single Responsibility - este router solo gestiona el listado y detalle de empleos
router = APIRouter(prefix="/jobs", tags=["Empleos"])


@router.get("/")
def list_jobs(
    city: Optional[str] = Query(None),
    modality: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # GRASP: Controlador - delega la consulta al Repository
    job_repo = JobRepository(db)
    jobs = job_repo.find_all(city=city, modality=modality)
    # GRASP: Fabricación Pura - DTOFactory transforma los datos para la respuesta
    return [DTOFactory.job_dto_to_dict(DTOFactory.create_job_dto(j)) for j in jobs]


@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    job_repo = JobRepository(db)
    job = job_repo.find_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Empleo no encontrado")
    return DTOFactory.job_dto_to_dict(DTOFactory.create_job_dto(job))
