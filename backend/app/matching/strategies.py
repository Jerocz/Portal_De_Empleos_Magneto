"""
Patrón de Diseño: Strategy (Comportamiento)
Permite intercambiar algoritmos de matching sin modificar el código cliente.
"""
from abc import ABC, abstractmethod


# SOLID: Interface Segregation - la interfaz define solo el contrato mínimo necesario
# SOLID: Open/Closed - se puede extender con nuevas estrategias sin modificar las existentes
class MatchingStrategy(ABC):
    """Clase base abstracta para todas las estrategias de matching."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        """
        Calcula el score de compatibilidad entre un perfil de usuario y un empleo.
        Retorna (score 0-100, explicacion en texto).
        """
        pass


# SOLID: Single Responsibility - solo evalúa compatibilidad de skills
# GRASP: Experto en Información - posee todo el conocimiento para calcular coincidencias de skills
class SkillMatchingStrategy(MatchingStrategy):
    """Evalúa qué porcentaje de las skills requeridas tiene el candidato."""

    @property
    def name(self) -> str:
        return "skills"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        user_skills = user_profile.get("skills") or []
        job_skills = job.get("skills_required") or []

        if not job_skills:
            return 0.0, "Skills: el empleo no tiene skills definidas"
        if not user_skills:
            return 0.0, "Skills: tu perfil no tiene skills registradas"

        user_set = {s.lower().strip() for s in user_skills}
        job_set = {s.lower().strip() for s in job_skills}

        coincidencias = user_set & job_set
        score = round(len(coincidencias) / len(job_set) * 100, 2)

        faltantes = sorted(job_set - coincidencias)
        if coincidencias:
            msg = (
                f"Skills: coincides en [{', '.join(sorted(coincidencias))}]; "
                f"faltan: [{', '.join(faltantes) or 'ninguna'}]"
            )
        else:
            msg = f"Skills: sin coincidencias con [{', '.join(sorted(job_set))}]"

        return score, msg


# SOLID: Single Responsibility - solo evalúa compatibilidad salarial
# GRASP: Experto en Información - conoce cómo calcular solapamiento de rangos
class SalaryMatchingStrategy(MatchingStrategy):
    """Evalúa la compatibilidad entre el rango salarial del candidato y el del empleo."""

    @property
    def name(self) -> str:
        return "salary"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        u_min = user_profile.get("salary_min_cop") or 0
        u_max = user_profile.get("salary_max_cop") or 0
        j_min = job.get("salary_min_cop") or 0
        j_max = job.get("salary_max_cop") or 0

        # Si alguna parte no tiene datos, score neutro para no penalizar
        if not j_min and not j_max:
            return 50.0, "Salario: el empleo no especifica rango salarial"
        if not u_min and not u_max:
            return 50.0, "Salario: no has especificado tu expectativa salarial"

        # Extrapolar si solo hay un límite
        effective_j_max = j_max if j_max else j_min * 2
        effective_u_max = u_max if u_max else u_min * 2

        overlap_start = max(u_min, j_min)
        overlap_end = min(effective_u_max, effective_j_max)

        j_min_k = j_min // 1000
        j_max_k = effective_j_max // 1000

        if overlap_start > overlap_end:
            if u_min > effective_j_max:
                return 0.0, (
                    f"Salario: tu mínimo ({u_min // 1000}K COP) supera el "
                    f"máximo del empleo ({j_max_k}K COP)"
                )
            return 20.0, f"Salario: el empleo ({j_min_k}K-{j_max_k}K COP) está por debajo de tu expectativa"

        total_range = effective_j_max - j_min if effective_j_max > j_min else 1
        overlap = overlap_end - overlap_start
        score = round(min((overlap / total_range) * 100, 100), 2)
        return score, f"Salario: rango del empleo {j_min_k}K-{j_max_k}K COP, compatible con tu expectativa"


# SOLID: Single Responsibility - solo evalúa compatibilidad de modalidad
# GRASP: Experto en Información - conoce las reglas de compatibilidad de modalidad
class ModalityMatchingStrategy(MatchingStrategy):
    """Evalúa si la modalidad del empleo coincide con la preferida por el candidato."""

    # Mapa de compatibilidad parcial: hybrid es parcialmente compatible con ambas modalidades
    _PARTIAL_SCORE = 50.0

    @property
    def name(self) -> str:
        return "modality"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        user_mod = (user_profile.get("modality") or "").lower().strip()
        job_mod = (job.get("modality") or "").lower().strip()

        if not user_mod or not job_mod:
            return 50.0, "Modalidad: sin preferencia definida"

        if user_mod == job_mod:
            return 100.0, f"Modalidad: coincide perfectamente ({job_mod})"

        # hybrid es parcialmente compatible con remote y on-site
        if "hybrid" in (user_mod, job_mod):
            return self._PARTIAL_SCORE, (
                f"Modalidad: parcialmente compatible "
                f"(tú prefieres {user_mod}, empleo es {job_mod})"
            )

        return 0.0, f"Modalidad: no coincide (tú: {user_mod}, empleo: {job_mod})"


# SOLID: Open/Closed - se pueden agregar estrategias sin modificar esta clase
# GRASP: Variaciones Protegidas - aísla al resto del sistema de cambios en el algoritmo de matching
# GRASP: Indirección - actúa como mediador entre el servicio y las estrategias concretas
class CompositeMatchingStrategy:
    """
    Combina múltiples estrategias con pesos ponderados para generar un score final.
    Por defecto: Skills 60%, Salario 25%, Modalidad 15%.
    """

    DEFAULT_WEIGHTS: dict[str, float] = {
        "skills": 0.60,
        "salary": 0.25,
        "modality": 0.15,
    }

    def __init__(
        self,
        strategies: list[tuple[MatchingStrategy, float]] | None = None,
    ) -> None:
        if strategies is None:
            self._strategies: list[tuple[MatchingStrategy, float]] = [
                (SkillMatchingStrategy(), self.DEFAULT_WEIGHTS["skills"]),
                (SalaryMatchingStrategy(), self.DEFAULT_WEIGHTS["salary"]),
                (ModalityMatchingStrategy(), self.DEFAULT_WEIGHTS["modality"]),
            ]
        else:
            self._strategies = strategies

    # SOLID: Liskov Substitution - cualquier MatchingStrategy es usable aquí sin condiciones
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        """Retorna (score ponderado 0-100, explicacion detallada de cada criterio)."""
        total_weight = sum(w for _, w in self._strategies)
        weighted_score = 0.0
        explanations: list[str] = []

        for strategy, weight in self._strategies:
            score, msg = strategy.calculate(user_profile, job)
            weighted_score += score * (weight / total_weight)
            explanations.append(msg)

        return round(weighted_score, 2), " | ".join(explanations)
