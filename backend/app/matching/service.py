from datetime import date
from sqlalchemy.orm import Session

from app.matching.strategies import CompositeMatchingStrategy
from app.repositories.job_repository import JobRepository
from app.repositories.match_repository import MatchRepository


class MatchingService:
    """Calcula y guarda el ranking de empleos para un usuario."""

    def __init__(self, db: Session, strategy: CompositeMatchingStrategy | None = None) -> None:
        self._job_repo = JobRepository(db)
        self._match_repo = MatchRepository(db)
        self._strategy = strategy or CompositeMatchingStrategy()
        self._db = db

    def run_matching(self, user_id: int, user_profile: dict) -> dict:
        """
        Recalcula el matching completo para el usuario.
        Guarda TODOS los empleos con su puntaje (0-100) para generar el ranking.
        Retorna un dict con totales para el mensaje de respuesta.
        """
        jobs = self._job_repo.find_all(limit=200)

        # Borra matches anteriores para obtener resultados frescos
        self._match_repo.delete_by_user(user_id)

        today = date.today()
        con_afinidad = 0

        for job in jobs:
            score, explanation = self._strategy.calculate(user_profile, job)
            self._match_repo.create(user_id, job["id"], score, explanation, today)
            if score >= 25:
                con_afinidad += 1

        self._db.commit()
        return {"total": len(jobs), "con_afinidad": con_afinidad}
