from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from datetime import date
from app.deps import get_db
from app.security import get_current_user

router = APIRouter(prefix="/matches", tags=["Matching"])


def calcular_score(user_skills: list, job_skills: list) -> tuple[float, str]:
    """
    Compara las skills del usuario con las requeridas por el trabajo.
    Retorna (score de 0-100, explicacion).
    """
    if not job_skills:
        return 0.0, "El empleo no tiene skills definidas"

    user_set = set(s.lower().strip() for s in user_skills)
    job_set = set(s.lower().strip() for s in job_skills)

    coincidencias = user_set & job_set
    score = round(len(coincidencias) / len(job_set) * 100, 2)

    if coincidencias:
        explicacion = f"Coincides en: {', '.join(sorted(coincidencias))}. Faltan: {', '.join(sorted(job_set - coincidencias)) or 'ninguna'}"
    else:
        explicacion = f"No coincides con ninguna skill requerida: {', '.join(sorted(job_set))}"

    return score, explicacion


@router.post("/run")
def run_matching(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Compara el perfil del usuario con todos los empleos y guarda los resultados."""
    profile = db.execute(
        text("SELECT skills FROM profiles WHERE user_id = :uid"),
        {"uid": current_user["id"]}
    ).fetchone()

    if not profile or not profile.skills:
        raise HTTPException(status_code=400, detail="Completa tu perfil con tus skills primero")

    user_skills = json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills

    jobs = db.execute(text("SELECT id, title, company, skills_required FROM jobs")).fetchall()

    today = date.today()
    nuevos_matches = 0

    for job in jobs:
        job_skills = json.loads(job.skills_required) if isinstance(job.skills_required, str) else job.skills_required or []
        score, explicacion = calcular_score(user_skills, job_skills)

        # Solo guarda si el score es mayor a 0
        if score > 0:
            existing = db.execute(
                text("SELECT id FROM job_matches WHERE user_id = :uid AND job_id = :jid AND run_date = :d"),
                {"uid": current_user["id"], "jid": job.id, "d": today}
            ).fetchone()

            if not existing:
                db.execute(
                    text("""INSERT INTO job_matches (user_id, job_id, score, explanation, run_date, created_at)
                            VALUES (:uid, :jid, :score, :exp, :d, NOW())"""),
                    {"uid": current_user["id"], "jid": job.id, "score": score, "exp": explicacion, "d": today}
                )
                nuevos_matches += 1

    db.commit()
    return {"message": f"Matching completado. {nuevos_matches} nuevos matches encontrados hoy."}


@router.get("/")
def get_my_matches(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retorna los mejores matches del usuario, ordenados por score."""
    rows = db.execute(
        text("""
            SELECT jm.id, jm.score, jm.explanation, jm.run_date,
                   j.id as job_id, j.title, j.company, j.city, j.modality,
                   j.salary_min_cop, j.salary_max_cop, j.skills_required
            FROM job_matches jm
            JOIN jobs j ON j.id = jm.job_id
            WHERE jm.user_id = :uid
            ORDER BY jm.score DESC
            LIMIT 20
        """),
        {"uid": current_user["id"]}
    ).fetchall()

    result = []
    for row in rows:
        m = dict(row._mapping)
        m["skills_required"] = json.loads(m["skills_required"]) if isinstance(m["skills_required"], str) else m["skills_required"] or []
        result.append(m)

    return result
