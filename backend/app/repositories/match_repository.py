"""
Patrón de Diseño: Repository
Encapsula toda la lógica de acceso a datos de la entidad JobMatch.
"""
import json
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


# SOLID: Single Responsibility - solo gestiona acceso a datos de matches
# GRASP: Alta Cohesión - todas las operaciones están relacionadas con job_matches
class MatchRepository:
    """Gestiona el acceso a la tabla `job_matches` en la base de datos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_user(self, user_id: int, limit: int = 20) -> list[dict]:
        rows = self._db.execute(
            text("""
                SELECT jm.id, jm.score, jm.explanation, jm.run_date,
                       j.id AS job_id, j.title, j.company, j.city, j.modality,
                       j.salary_min_cop, j.salary_max_cop, j.skills_required
                FROM job_matches jm
                JOIN jobs j ON j.id = jm.job_id
                WHERE jm.user_id = :uid
                ORDER BY jm.score DESC
                LIMIT :lim
            """),
            {"uid": user_id, "lim": int(limit)},
        ).fetchall()

        result = []
        for row in rows:
            m = dict(row._mapping)
            raw = m.get("skills_required")
            m["skills_required"] = json.loads(raw) if isinstance(raw, str) else (raw or [])
            result.append(m)
        return result

    def find_by_user_job_date(
        self, user_id: int, job_id: int, run_date: date
    ) -> Optional[dict]:
        row = self._db.execute(
            text(
                "SELECT id FROM job_matches "
                "WHERE user_id = :uid AND job_id = :jid AND run_date = :d"
            ),
            {"uid": user_id, "jid": job_id, "d": run_date},
        ).fetchone()
        return dict(row._mapping) if row else None

    def create(
        self,
        user_id: int,
        job_id: int,
        score: float,
        explanation: str,
        run_date: date,
    ) -> None:
        self._db.execute(
            text("""
                INSERT INTO job_matches
                    (user_id, job_id, score, explanation, run_date, created_at)
                VALUES (:uid, :jid, :score, :exp, :d, NOW())
            """),
            {
                "uid": user_id,
                "jid": job_id,
                "score": score,
                "exp": explanation,
                "d": run_date,
            },
        )

    def find_notifications(
        self, user_id: int, min_score: float, limit: int = 10
    ) -> list[dict]:
        rows = self._db.execute(
            text("""
                SELECT jm.id, jm.score, jm.explanation, jm.run_date, jm.created_at,
                       j.title, j.company, j.city, j.modality
                FROM job_matches jm
                JOIN jobs j ON j.id = jm.job_id
                WHERE jm.user_id = :uid AND jm.score >= :min_score
                ORDER BY jm.created_at DESC
                LIMIT :lim
            """),
            {"uid": user_id, "min_score": min_score, "lim": int(limit)},
        ).fetchall()
        return [dict(r._mapping) for r in rows]
