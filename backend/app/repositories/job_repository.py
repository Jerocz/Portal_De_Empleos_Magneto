"""
Patrón de Diseño: Repository
Encapsula toda la lógica de acceso a datos de la entidad Job.
"""
import json
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


# SOLID: Single Responsibility - solo gestiona acceso a datos de empleos
# GRASP: Experto en Información - conoce la estructura de la tabla jobs y cómo parsear sus campos
class JobRepository:
    """Gestiona el acceso a la tabla `jobs` en la base de datos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _parse_skills(self, job: dict) -> dict:
        """Deserializa el campo skills_required de JSON a lista."""
        raw = job.get("skills_required")
        if isinstance(raw, str):
            job["skills_required"] = json.loads(raw)
        elif not raw:
            job["skills_required"] = []
        return job

    def find_all(
        self,
        city: Optional[str] = None,
        modality: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        query = "SELECT * FROM jobs WHERE 1=1"
        params: dict = {}

        if city:
            query += " AND city LIKE :city"
            params["city"] = f"%{city}%"
        if modality:
            query += " AND modality = :modality"
            params["modality"] = modality

        query += f" ORDER BY posted_at DESC LIMIT {int(limit)}"
        rows = self._db.execute(text(query), params).fetchall()
        return [self._parse_skills(dict(r._mapping)) for r in rows]

    def find_by_id(self, job_id: int) -> dict | None:
        row = self._db.execute(
            text("SELECT * FROM jobs WHERE id = :id"), {"id": job_id}
        ).fetchone()
        if not row:
            return None
        return self._parse_skills(dict(row._mapping))

    def create(
        self,
        title: str,
        company: str,
        city: Optional[str],
        modality: Optional[str],
        description: Optional[str],
        salary_min_cop: Optional[int],
        salary_max_cop: Optional[int],
        skills_required: list,
        posted_by: int,
    ) -> dict:
        self._db.execute(
            text(
                "INSERT INTO jobs (title, company, city, modality, description, "
                "salary_min_cop, salary_max_cop, skills_required, posted_by, posted_at) "
                "VALUES (:title, :company, :city, :modality, :desc, "
                ":smin, :smax, :skills, :posted_by, NOW())"
            ),
            {
                "title": title, "company": company, "city": city,
                "modality": modality, "desc": description,
                "smin": salary_min_cop, "smax": salary_max_cop,
                "skills": json.dumps(skills_required), "posted_by": posted_by,
            },
        )
        self._db.commit()
        row = self._db.execute(text("SELECT LAST_INSERT_ID() AS id")).fetchone()
        return self.find_by_id(row.id)

    def find_by_employer(self, user_id: int) -> list[dict]:
        rows = self._db.execute(
            text("SELECT * FROM jobs WHERE posted_by = :uid ORDER BY posted_at DESC"),
            {"uid": user_id},
        ).fetchall()
        return [self._parse_skills(dict(r._mapping)) for r in rows]
