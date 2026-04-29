"""
Patrón de Diseño: Factory
DTOFactory construye los objetos de transferencia de datos (DTO) que la API retorna.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional


# --- DTOs (Data Transfer Objects) ---

@dataclass
class UserProfileDTO:
    id: int
    email: str
    full_name: str
    location_city: Optional[str] = None
    modality: Optional[str] = None
    salary_min_cop: Optional[int] = None
    salary_max_cop: Optional[int] = None
    years_exp: Optional[int] = None
    skills: list[str] = field(default_factory=list)


@dataclass
class JobDTO:
    id: int
    title: str
    company: str
    city: str
    modality: str
    salary_min_cop: Optional[int] = None
    salary_max_cop: Optional[int] = None
    skills_required: list[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class MatchResultDTO:
    id: int
    job_id: int
    title: str
    company: str
    city: str
    modality: str
    score: float
    explanation: str
    run_date: str
    salary_min_cop: Optional[int] = None
    salary_max_cop: Optional[int] = None
    skills_required: list[str] = field(default_factory=list)


# SOLID: Single Responsibility - solo construye DTOs, no hace acceso a datos ni lógica de negocio
# SOLID: Dependency Inversion - los routers dependen de esta abstracción en lugar de construir dicts manualmente
# GRASP: Creador - cumple los criterios de creador: contiene los datos necesarios para crear los DTOs
# GRASP: Fabricación Pura - no corresponde a ninguna entidad del dominio real; existe solo para desacoplar capas
class DTOFactory:
    """Construye los objetos de respuesta (DTOs) de la API a partir de dicts de base de datos."""

    @staticmethod
    def create_user_profile_dto(user: dict, profile: Optional[dict]) -> UserProfileDTO:
        return UserProfileDTO(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            location_city=profile.get("location_city") if profile else None,
            modality=profile.get("modality") if profile else None,
            salary_min_cop=profile.get("salary_min_cop") if profile else None,
            salary_max_cop=profile.get("salary_max_cop") if profile else None,
            years_exp=profile.get("years_exp") if profile else None,
            skills=profile.get("skills", []) if profile else [],
        )

    @staticmethod
    def create_job_dto(job: dict) -> JobDTO:
        return JobDTO(
            id=job["id"],
            title=job["title"],
            company=job["company"],
            city=job.get("city", ""),
            modality=job.get("modality", ""),
            salary_min_cop=job.get("salary_min_cop"),
            salary_max_cop=job.get("salary_max_cop"),
            skills_required=job.get("skills_required", []),
            description=job.get("description"),
        )

    @staticmethod
    def create_match_result_dto(match: dict) -> MatchResultDTO:
        return MatchResultDTO(
            id=match["id"],
            job_id=match["job_id"],
            title=match["title"],
            company=match["company"],
            city=match.get("city", ""),
            modality=match.get("modality", ""),
            salary_min_cop=match.get("salary_min_cop"),
            salary_max_cop=match.get("salary_max_cop"),
            skills_required=match.get("skills_required", []),
            score=float(match["score"]),
            explanation=match.get("explanation", ""),
            run_date=str(match.get("run_date", "")),
        )

    # --- Serialización a dict para respuestas JSON de FastAPI ---

    @staticmethod
    def user_profile_dto_to_dict(dto: UserProfileDTO) -> dict:
        has_profile = any([
            dto.location_city, dto.modality, dto.salary_min_cop, dto.skills
        ])
        return {
            "id": dto.id,
            "email": dto.email,
            "full_name": dto.full_name,
            "profile": {
                "location_city": dto.location_city,
                "modality": dto.modality,
                "salary_min_cop": dto.salary_min_cop,
                "salary_max_cop": dto.salary_max_cop,
                "years_exp": dto.years_exp,
                "skills": dto.skills,
            } if has_profile else None,
        }

    @staticmethod
    def job_dto_to_dict(dto: JobDTO) -> dict:
        return {
            "id": dto.id,
            "title": dto.title,
            "company": dto.company,
            "city": dto.city,
            "modality": dto.modality,
            "salary_min_cop": dto.salary_min_cop,
            "salary_max_cop": dto.salary_max_cop,
            "skills_required": dto.skills_required,
            "description": dto.description,
        }

    @staticmethod
    def match_dto_to_dict(dto: MatchResultDTO) -> dict:
        return {
            "id": dto.id,
            "job_id": dto.job_id,
            "title": dto.title,
            "company": dto.company,
            "city": dto.city,
            "modality": dto.modality,
            "salary_min_cop": dto.salary_min_cop,
            "salary_max_cop": dto.salary_max_cop,
            "skills_required": dto.skills_required,
            "score": dto.score,
            "explanation": dto.explanation,
            "run_date": dto.run_date,
        }
