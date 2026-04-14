from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
import json
from app.deps import get_db
from app.security import get_current_user

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
    profile = db.execute(
        text("SELECT * FROM profiles WHERE user_id = :uid"),
        {"uid": current_user["id"]}
    ).fetchone()

    user_data = {
        "id": current_user["id"],
        "email": current_user["email"],
        "full_name": current_user["full_name"],
    }

    if profile:
        p = dict(profile._mapping)
        p["skills"] = json.loads(p["skills"]) if isinstance(p["skills"], str) else p["skills"] or []
        user_data["profile"] = p
    else:
        user_data["profile"] = None

    return user_data


@router.put("/")
def update_profile(data: ProfileUpdate, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.execute(
        text("SELECT user_id FROM profiles WHERE user_id = :uid"),
        {"uid": current_user["id"]}
    ).fetchone()

    skills_json = json.dumps(data.skills) if data.skills is not None else json.dumps([])

    if existing:
        db.execute(
            text("""UPDATE profiles SET
                location_city = :city,
                modality = :mod,
                salary_min_cop = :smin,
                salary_max_cop = :smax,
                years_exp = :yexp,
                skills = :skills,
                updated_at = NOW()
                WHERE user_id = :uid"""),
            {
                "city": data.location_city,
                "mod": data.modality,
                "smin": data.salary_min_cop,
                "smax": data.salary_max_cop,
                "yexp": data.years_exp,
                "skills": skills_json,
                "uid": current_user["id"]
            }
        )
    else:
        db.execute(
            text("""INSERT INTO profiles
                (user_id, location_city, modality, salary_min_cop, salary_max_cop, years_exp, skills, updated_at)
                VALUES (:uid, :city, :mod, :smin, :smax, :yexp, :skills, NOW())"""),
            {
                "uid": current_user["id"],
                "city": data.location_city,
                "mod": data.modality,
                "smin": data.salary_min_cop,
                "smax": data.salary_max_cop,
                "yexp": data.years_exp,
                "skills": skills_json,
            }
        )

    db.commit()
    return {"message": "Perfil actualizado correctamente"}
