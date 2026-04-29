"""
Servicio de Matching: orquesta la ejecución del algoritmo de matching.
"""
from datetime import date
from sqlalchemy.orm import Session

from app.matching.strategies import CompositeMatchingStrategy
from app.repositories.job_repository import JobRepository
from app.repositories.match_repository import MatchRepository


# SOLID: Single Responsibility - solo coordina el proceso de matching
# GRASP: Controlador - orquesta la operación entre repositories y estrategias
class MatchingService:
    """Coordina la ejecución de matching entre un usuario y todos los empleos disponibles."""

    def __init__(
        self,
        db: Session,
        strategy: CompositeMatchingStrategy | None = None,
    ) -> None:
        # SOLID: Dependency Inversion - depende de abstracciones, no de implementaciones concretas
        self._job_repo = JobRepository(db)
        self._match_repo = MatchRepository(db)
        self._strategy = strategy or CompositeMatchingStrategy()
        self._db = db

    def run_matching(self, user_id: int, user_profile: dict) -> int:
        """
        Ejecuta el matching completo para un usuario.
        Retorna la cantidad de nuevos matches guardados hoy.
        """
        jobs = self._job_repo.find_all(limit=200)
        today = date.today()
        nuevos_matches = 0

        for job in jobs:
            score, explanation = self._strategy.calculate(user_profile, job)

            if score > 0:
                existing = self._match_repo.find_by_user_job_date(user_id, job["id"], today)
                if not existing:
                    self._match_repo.create(user_id, job["id"], score, explanation, today)
                    nuevos_matches += 1

        self._db.commit()
        return nuevos_matches
