from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from app.deps import get_db
from app.security import get_current_user
from app.repositories.job_repository import JobRepository
from app.factories.dto_factory import DTOFactory

router = APIRouter(prefix="/jobs", tags=["Empleos"])


class JobCreate(BaseModel):
    title: str
    company: str
    city: Optional[str] = None
    modality: Optional[str] = None
    description: Optional[str] = None
    salary_min_cop: Optional[int] = None
    salary_max_cop: Optional[int] = None
    skills_required: Optional[List[str]] = []


@router.get("/my-jobs")
def my_jobs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Solo contratantes pueden ver sus empleos")
    job_repo = JobRepository(db)
    jobs = job_repo.find_by_employer(current_user["id"])
    return [DTOFactory.job_dto_to_dict(DTOFactory.create_job_dto(j)) for j in jobs]


@router.get("/")
def list_jobs(
    city: Optional[str] = Query(None),
    modality: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    job_repo = JobRepository(db)
    jobs = job_repo.find_all(city=city, modality=modality)
    return [DTOFactory.job_dto_to_dict(DTOFactory.create_job_dto(j)) for j in jobs]


@router.post("/")
def create_job(
    data: JobCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Solo contratantes pueden publicar empleos")
    job_repo = JobRepository(db)
    job = job_repo.create(
        title=data.title,
        company=data.company,
        city=data.city,
        modality=data.modality,
        description=data.description,
        salary_min_cop=data.salary_min_cop,
        salary_max_cop=data.salary_max_cop,
        skills_required=data.skills_required or [],
        posted_by=current_user["id"],
    )
    return DTOFactory.job_dto_to_dict(DTOFactory.create_job_dto(job))


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


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user.get("role") != "employer":
        raise HTTPException(status_code=403, detail="Solo contratantes pueden eliminar empleos")
    job_repo = JobRepository(db)
    deleted = job_repo.delete(job_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Empleo no encontrado o no te pertenece")
    return {"message": "Vacante eliminada correctamente"}
