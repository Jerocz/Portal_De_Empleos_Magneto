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

    def delete(self, job_id: int, owner_id: int) -> bool:
        """Elimina un empleo solo si pertenece al owner. Retorna True si se borró."""
        result = self._db.execute(
            text("DELETE FROM jobs WHERE id = :id AND posted_by = :owner"),
            {"id": job_id, "owner": owner_id},
        )
        self._db.commit()
        return result.rowcount > 0

    def update(
        self,
        job_id: int,
        owner_id: int,
        title: str,
        company: str,
        city: str | None,
        modality: str | None,
        description: str | None,
        salary_min_cop: int | None,
        salary_max_cop: int | None,
        skills_required: list,
    ) -> dict | None:
        """Actualiza una vacante si pertenece al owner. Retorna el empleo actualizado."""
        result = self._db.execute(
            text("""
                UPDATE jobs SET
                    title          = :title,
                    company        = :company,
                    city           = :city,
                    modality       = :modality,
                    description    = :desc,
                    salary_min_cop = :smin,
                    salary_max_cop = :smax,
                    skills_required = :skills
                WHERE id = :id AND posted_by = :owner
            """),
            {
                "title": title, "company": company, "city": city,
                "modality": modality, "desc": description,
                "smin": salary_min_cop, "smax": salary_max_cop,
                "skills": json.dumps(skills_required), "id": job_id, "owner": owner_id,
            },
        )
        self._db.commit()
        if result.rowcount == 0:
            return None
        return self.find_by_id(job_id)
