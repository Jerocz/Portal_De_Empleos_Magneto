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
