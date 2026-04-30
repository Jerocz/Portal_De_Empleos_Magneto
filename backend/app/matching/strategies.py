"""
Patrón de Diseño: Strategy (Comportamiento)
Sistema de puntos: cada campo que coincide suma 25 pts (máx 100).
Las explicaciones usan prefijo 'OK:' o 'NO:' para que el frontend
pueda determinar si cada criterio coincidió sin ambigüedad.

Comparaciones normalizadas: sin tildes, minúsculas, sin espacios extra,
para que "Medellín", "medellin", "MEDELLÍN" sean equivalentes.
"""
from abc import ABC, abstractmethod
import unicodedata


def _normalize(text: str) -> str:
    """Convierte a minúsculas, elimina tildes/diacríticos y espacios extra."""
    if not text:
        return ""
    # Descompone caracteres con tilde (á → a + combining accent) y descarta el acento
    nfkd = unicodedata.normalize("NFKD", text)
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_tildes.lower().strip()


class MatchingStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        """Retorna (puntos aportados 0 o 25, descripción del resultado).
        El string comienza con 'OK:' si coincide, o 'NO:' si no coincide."""
        pass


class CityMatchStrategy(MatchingStrategy):
    """Ciudad del empleo coincide (o es remoto): +25 pts."""

    @property
    def name(self) -> str:
        return "city"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        job_modality = _normalize(job.get("modality") or "")
        if job_modality == "remote":
            return 25.0, "OK:Ciudad: trabajo remoto (ubicación flexible)"

        user_city = _normalize(user_profile.get("location_city") or "")
        job_city  = _normalize(job.get("city") or "")

        if not user_city or not job_city:
            return 0.0, "NO:Ciudad: sin datos de ubicación"

        if user_city == job_city or user_city in job_city or job_city in user_city:
            # Mostrar el nombre original (sin normalizar) para mejor legibilidad
            display = (job.get("city") or "").strip().title()
            return 25.0, f"OK:Ciudad: {display}"

        display = (job.get("city") or "").strip().title()
        return 0.0, f"NO:Ciudad: {display} (diferente a la tuya)"


class ModalityMatchStrategy(MatchingStrategy):
    """Modalidad del empleo coincide con preferencia del usuario: +25 pts."""

    @property
    def name(self) -> str:
        return "modality"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        user_mod = _normalize(user_profile.get("modality") or "")
        job_mod  = _normalize(job.get("modality") or "")

        if not user_mod or not job_mod:
            return 0.0, "NO:Modalidad: sin preferencia definida"

        if user_mod == job_mod:
            return 25.0, f"OK:Modalidad: {job_mod}"

        if "hybrid" in (user_mod, job_mod):
            return 25.0, f"OK:Modalidad: {job_mod} (compatible con híbrido)"

        return 0.0, f"NO:Modalidad: {job_mod} (no coincide con tu preferencia)"


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
            return 0.0, "NO:Salario: el empleo no especifica salario"
        if not u_min and not u_max:
            return 0.0, "NO:Salario: no definiste expectativa salarial"

        eff_j_max = j_max or j_min * 2
        eff_u_max = u_max or u_min * 2

        overlap = min(eff_u_max, eff_j_max) - max(u_min, j_min)
        j_min_k  = j_min // 1000
        j_max_k  = eff_j_max // 1000

        if overlap >= 0:
            return 25.0, f"OK:Salario: {j_min_k}K–{j_max_k}K COP (dentro de tu rango)"

        return 0.0, f"NO:Salario: {j_min_k}K–{j_max_k}K COP (fuera de tu rango)"


class SkillsMatchStrategy(MatchingStrategy):
    """Al menos 1 skill del usuario coincide con las requeridas: +25 pts."""

    @property
    def name(self) -> str:
        return "skills"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        # Normalizar cada skill individualmente
        user_skills = {_normalize(s) for s in (user_profile.get("skills") or []) if s}
        job_skills  = {_normalize(s) for s in (job.get("skills_required") or []) if s}

        if not job_skills:
            return 0.0, "NO:Skills: el empleo no lista skills requeridas"
        if not user_skills:
            return 0.0, "NO:Skills: no tienes skills en tu perfil"

        coincidencias = sorted(user_skills & job_skills)
        faltantes     = sorted(job_skills - user_skills)

        if coincidencias:
            return 25.0, (
                f"OK:Skills: {', '.join(coincidencias)} "
                f"(faltan: {', '.join(faltantes) or 'ninguna'})"
            )

        return 0.0, f"NO:Skills: sin coincidencias (requiere: {', '.join(sorted(job_skills))})"


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
