"""
Patrón de Diseño: Strategy (Comportamiento)
Sistema de puntos: cada campo que coincide suma 25 pts (máx 100).
"""
from abc import ABC, abstractmethod


class MatchingStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        """Retorna (puntos aportados 0 o 25, descripción del resultado)."""
        pass


class CityMatchStrategy(MatchingStrategy):
    """Ciudad del empleo coincide (o es remoto): +25 pts."""

    @property
    def name(self) -> str:
        return "city"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        job_modality = (job.get("modality") or "").lower().strip()
        if job_modality == "remote":
            return 25.0, "Ciudad: trabajo remoto (ubicación flexible)"

        user_city = (user_profile.get("location_city") or "").lower().strip()
        job_city = (job.get("city") or "").lower().strip()

        if not user_city or not job_city:
            return 0.0, "Ciudad: sin datos de ubicación"

        if user_city == job_city or user_city in job_city or job_city in user_city:
            return 25.0, f"Ciudad: {job_city.title()}"

        return 0.0, f"Ciudad: {job_city.title()} (diferente a la tuya)"


class ModalityMatchStrategy(MatchingStrategy):
    """Modalidad del empleo coincide con preferencia del usuario: +25 pts."""

    @property
    def name(self) -> str:
        return "modality"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        user_mod = (user_profile.get("modality") or "").lower().strip()
        job_mod = (job.get("modality") or "").lower().strip()

        if not user_mod or not job_mod:
            return 0.0, "Modalidad: sin preferencia definida"

        if user_mod == job_mod:
            return 25.0, f"Modalidad: {job_mod}"

        if "hybrid" in (user_mod, job_mod):
            return 25.0, f"Modalidad: {job_mod} (compatible con híbrido)"

        return 0.0, f"Modalidad: {job_mod} (no coincide con tu preferencia)"


class SalaryMatchStrategy(MatchingStrategy):
    """Rango salarial del empleo cae dentro del rango del usuario: +25 pts."""

    @property
    def name(self) -> str:
        return "salary"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        u_min = user_profile.get("salary_min_cop") or 0
        u_max = user_profile.get("salary_max_cop") or 0
        j_min = job.get("salary_min_cop") or 0
        j_max = job.get("salary_max_cop") or 0

        if not j_min and not j_max:
            return 0.0, "Salario: el empleo no especifica salario"
        if not u_min and not u_max:
            return 0.0, "Salario: no definiste expectativa salarial"

        eff_j_max = j_max or j_min * 2
        eff_u_max = u_max or u_min * 2

        overlap = min(eff_u_max, eff_j_max) - max(u_min, j_min)
        j_min_k = j_min // 1000
        j_max_k = eff_j_max // 1000

        if overlap >= 0:
            return 25.0, f"Salario: {j_min_k}K–{j_max_k}K COP (dentro de tu rango)"

        return 0.0, f"Salario: {j_min_k}K–{j_max_k}K COP (fuera de tu rango)"


class SkillsMatchStrategy(MatchingStrategy):
    """Al menos 1 skill del usuario coincide con las requeridas: +25 pts."""

    @property
    def name(self) -> str:
        return "skills"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        user_skills = {s.lower().strip() for s in (user_profile.get("skills") or [])}
        job_skills = {s.lower().strip() for s in (job.get("skills_required") or [])}

        if not job_skills:
            return 0.0, "Skills: el empleo no lista skills requeridas"
        if not user_skills:
            return 0.0, "Skills: no tienes skills en tu perfil"

        coincidencias = sorted(user_skills & job_skills)
        faltantes = sorted(job_skills - user_skills)

        if coincidencias:
            return 25.0, f"Skills: {', '.join(coincidencias)} ✓ (faltan: {', '.join(faltantes) or 'ninguna'})"

        return 0.0, f"Skills: sin coincidencias (requiere: {', '.join(sorted(job_skills))})"


class CompositeMatchingStrategy:
    """
    Combina las 4 estrategias de puntos (máx 100 pts = 4 campos coincidentes).
    Ciudad 25 · Modalidad 25 · Salario 25 · Skills 25
    """

    def __init__(self) -> None:
        self._strategies: list[MatchingStrategy] = [
            CityMatchStrategy(),
            ModalityMatchStrategy(),
            SalaryMatchStrategy(),
            SkillsMatchStrategy(),
        ]

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        total = 0.0
        parts: list[str] = []

        for strategy in self._strategies:
            pts, msg = strategy.calculate(user_profile, job)
            total += pts
            parts.append(msg)

        return round(total, 2), " | ".join(parts)
