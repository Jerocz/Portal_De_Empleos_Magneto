from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import json
from app.deps import get_db
from app.security import get_current_user

router = APIRouter(prefix="/jobs", tags=["Empleos"])


@router.get("/")
def list_jobs(
    city: Optional[str] = Query(None),
    modality: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = "SELECT * FROM jobs WHERE 1=1"
    params = {}

    if city:
        query += " AND city LIKE :city"
        params["city"] = f"%{city}%"
    if modality:
        query += " AND modality = :modality"
        params["modality"] = modality

    query += " ORDER BY posted_at DESC LIMIT 50"
    rows = db.execute(text(query), params).fetchall()

    result = []
    for row in rows:
        job = dict(row._mapping)
        job["skills_required"] = json.loads(job["skills_required"]) if isinstance(job["skills_required"], str) else job["skills_required"] or []
        result.append(job)

    return result


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    row = db.execute(text("SELECT * FROM jobs WHERE id = :id"), {"id": job_id}).fetchone()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Empleo no encontrado")
    job = dict(row._mapping)
    job["skills_required"] = json.loads(job["skills_required"]) if isinstance(job["skills_required"], str) else job["skills_required"] or []
    return job
