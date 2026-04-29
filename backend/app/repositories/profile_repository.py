"""
Patrón de Diseño: Repository
Encapsula toda la lógica de acceso a datos de la entidad Profile.
"""
import json
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


# SOLID: Single Responsibility - solo gestiona acceso a datos de perfiles de usuario
# GRASP: Alta Cohesión - todas las operaciones son sobre la tabla profiles
class ProfileRepository:
    """Gestiona el acceso a la tabla `profiles` en la base de datos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_user_id(self, user_id: int) -> Optional[dict]:
        row = self._db.execute(
            text("SELECT * FROM profiles WHERE user_id = :uid"), {"uid": user_id}
        ).fetchone()
        if not row:
            return None
        p = dict(row._mapping)
        raw = p.get("skills")
        p["skills"] = json.loads(raw) if isinstance(raw, str) else (raw or [])
        return p

    def upsert(
        self,
        user_id: int,
        location_city: Optional[str],
        modality: Optional[str],
        salary_min_cop: Optional[int],
        salary_max_cop: Optional[int],
        years_exp: Optional[int],
        skills: list[str],
    ) -> None:
        skills_json = json.dumps(skills)
        existing = self._db.execute(
            text("SELECT user_id FROM profiles WHERE user_id = :uid"), {"uid": user_id}
        ).fetchone()

        if existing:
            self._db.execute(
                text("""
                    UPDATE profiles SET
                        location_city = :city,
                        modality      = :mod,
                        salary_min_cop = :smin,
                        salary_max_cop = :smax,
                        years_exp     = :yexp,
                        skills        = :skills,
                        updated_at    = NOW()
                    WHERE user_id = :uid
                """),
                {
                    "city": location_city, "mod": modality,
                    "smin": salary_min_cop, "smax": salary_max_cop,
                    "yexp": years_exp, "skills": skills_json, "uid": user_id,
                },
            )
        else:
            self._db.execute(
                text("""
                    INSERT INTO profiles
                        (user_id, location_city, modality, salary_min_cop,
                         salary_max_cop, years_exp, skills, updated_at)
                    VALUES (:uid, :city, :mod, :smin, :smax, :yexp, :skills, NOW())
                """),
                {
                    "uid": user_id, "city": location_city, "mod": modality,
                    "smin": salary_min_cop, "smax": salary_max_cop,
                    "yexp": years_exp, "skills": skills_json,
                },
            )
        self._db.commit()
