"""
Patrón Repository: encapsula acceso a datos de postulaciones.
"""
import json
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text


class ApplicationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def already_applied(self, job_id: int, employee_id: int) -> bool:
        row = self._db.execute(
            text("SELECT id FROM applications WHERE job_id=:j AND employee_id=:e"),
            {"j": job_id, "e": employee_id},
        ).fetchone()
        return row is not None

    def create(self, job_id: int, employee_id: int, message: Optional[str]) -> dict:
        self._db.execute(
            text(
                "INSERT INTO applications (job_id, employee_id, message, status) "
                "VALUES (:j, :e, :msg, 'pending')"
            ),
            {"j": job_id, "e": employee_id, "msg": message},
        )
        self._db.commit()
        return self.find_by_job_and_employee(job_id, employee_id)

    def find_by_job_and_employee(self, job_id: int, employee_id: int) -> Optional[dict]:
        row = self._db.execute(
            text("SELECT * FROM applications WHERE job_id=:j AND employee_id=:e"),
            {"j": job_id, "e": employee_id},
        ).fetchone()
        return dict(row._mapping) if row else None

    def find_by_employee(self, employee_id: int) -> list[dict]:
        """Todas las postulaciones del empleado con info del empleo."""
        rows = self._db.execute(
            text("""
                SELECT a.id, a.status, a.message, a.applied_at,
                       j.id AS job_id, j.title, j.company, j.city,
                       j.modality, j.salary_min_cop, j.salary_max_cop
                FROM applications a
                JOIN jobs j ON j.id = a.job_id
                WHERE a.employee_id = :e
                ORDER BY a.applied_at DESC
            """),
            {"e": employee_id},
        ).fetchall()
        return [dict(r._mapping) for r in rows]

    def find_by_employer(self, employer_id: int) -> list[dict]:
        """
        Todas las postulaciones a los empleos del empleador,
        incluyendo perfil completo del candidato.
        """
        rows = self._db.execute(
            text("""
                SELECT
                    a.id AS application_id,
                    a.status,
                    a.message,
                    a.applied_at,
                    j.id   AS job_id,
                    j.title AS job_title,
                    j.company,
                    u.id        AS candidate_id,
                    u.full_name AS candidate_name,
                    u.email     AS candidate_email,
                    p.location_city,
                    p.modality  AS candidate_modality,
                    p.salary_min_cop AS candidate_sal_min,
                    p.salary_max_cop AS candidate_sal_max,
                    p.years_exp,
                    p.skills
                FROM applications a
                JOIN jobs  j ON j.id = a.job_id
                JOIN users u ON u.id = a.employee_id
                LEFT JOIN profiles p ON p.user_id = a.employee_id
                WHERE j.posted_by = :emp
                ORDER BY a.applied_at DESC
            """),
            {"emp": employer_id},
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r._mapping)
            raw = d.get("skills")
            d["skills"] = json.loads(raw) if isinstance(raw, str) else (raw or [])
            d["applied_at"] = str(d["applied_at"])
            result.append(d)
        return result

    def update_status(self, application_id: int, employer_id: int, status: str) -> bool:
        """Cambia el estado (seen/rejected) — solo el empleador dueño del empleo puede hacerlo."""
        result = self._db.execute(
            text("""
                UPDATE applications a
                JOIN jobs j ON j.id = a.job_id
                SET a.status = :status
                WHERE a.id = :aid AND j.posted_by = :emp
            """),
            {"status": status, "aid": application_id, "emp": employer_id},
        )
        self._db.commit()
        return result.rowcount > 0

    def delete(self, application_id: int, employee_id: int) -> bool:
        """El empleado puede retirar su postulación."""
        result = self._db.execute(
            text("DELETE FROM applications WHERE id=:id AND employee_id=:e"),
            {"id": application_id, "e": employee_id},
        )
        self._db.commit()
        return result.rowcount > 0

    def update_status_with_employee(
        self, application_id: int, employer_id: int, status: str
    ) -> dict | None:
        """
        Cambia el estado y retorna {employee_id, job_title} para poder
        enviar la notificación WebSocket al empleado correcto.
        """
        row = self._db.execute(
            text("""
                SELECT a.employee_id, j.title AS job_title
                FROM applications a
                JOIN jobs j ON j.id = a.job_id
                WHERE a.id = :aid AND j.posted_by = :emp
            """),
            {"aid": application_id, "emp": employer_id},
        ).fetchone()

        if not row:
            return None

        self._db.execute(
            text("UPDATE applications SET status = :status WHERE id = :aid"),
            {"status": status, "aid": application_id},
        )
        self._db.commit()

        return {"employee_id": row.employee_id, "job_title": row.job_title}

    def find_by_id_for_employer(self, application_id: int, employer_id: int) -> dict | None:
        """Retorna la postulación solo si pertenece a una vacante del empleador."""
        row = self._db.execute(
            text("""
                SELECT a.id, a.employee_id, j.title AS job_title, j.company
                FROM applications a
                JOIN jobs j ON j.id = a.job_id
                WHERE a.id = :aid AND j.posted_by = :emp
            """),
            {"aid": application_id, "emp": employer_id},
        ).fetchone()
        return dict(row._mapping) if row else None

    def find_job_employer(self, job_id: int, db=None) -> dict | None:
        """Retorna el employer_id y título del empleo para notificaciones."""
        row = self._db.execute(
            text("""
                SELECT j.posted_by AS employer_id, j.title AS job_title
                FROM jobs j
                WHERE j.id = :jid
            """),
            {"jid": job_id},
        ).fetchone()
        return dict(row._mapping) if row else None

