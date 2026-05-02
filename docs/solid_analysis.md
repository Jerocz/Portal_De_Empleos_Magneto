# Análisis de Principios SOLID — Portal de Empleos Magneto

## Tabla resumen

| Principio | Sigla | Clase / Módulo | Descripción concreta |
|-----------|-------|----------------|----------------------|
| Single Responsibility | SRP | Cada repositorio, estrategia y factory | `JobRepository` solo accede a `jobs`; `CityMatchStrategy` solo evalúa ciudad; `DTOFactory` solo construye DTOs |
| Open/Closed | OCP | `CompositeMatchingStrategy` | Acepta nuevas estrategias sin modificar su código. Agregar `ExperienceMatchStrategy` no toca nada existente |
| Liskov Substitution | LSP | Las 4 estrategias concretas | `CityMatchStrategy`, `ModalityMatchStrategy`, `SalaryMatchStrategy` y `SkillsMatchStrategy` son intercambiables en `CompositeMatchingStrategy.calculate()` |
| Interface Segregation | ISP | `MatchingStrategy` (ABC) | Solo define `name` y `calculate()`. No obliga a implementar serialización, persistencia ni configuración |
| Dependency Inversion | DIP | Todos los routers | Los routers dependen de Repositories y DTOFactory, nunca de `db.execute(text(...))` directamente |

---

## SRP — Single Responsibility Principle

| Clase / Módulo | Única responsabilidad |
|---|---|
| `UserRepository` | Acceso a datos de la tabla `users` |
| `JobRepository` | Acceso a datos de la tabla `jobs` |
| `MatchRepository` | Acceso a datos de la tabla `job_matches` |
| `ProfileRepository` | Acceso a datos de la tabla `profiles` |
| `ApplicationRepository` | Acceso a datos de la tabla `applications` |
| `CityMatchStrategy` | Evaluar coincidencia de ciudad (con normalización) |
| `ModalityMatchStrategy` | Evaluar coincidencia de modalidad |
| `SalaryMatchStrategy` | Evaluar solapamiento de rango salarial |
| `SkillsMatchStrategy` | Evaluar intersección de habilidades normalizadas |
| `DTOFactory` | Construir objetos de respuesta de la API |
| `security.py` | Gestionar JWT y hashing de contraseñas |

```python
# SRP: ApplicationRepository solo gestiona postulaciones
class ApplicationRepository:
    def already_applied(self, job_id, employee_id) -> bool: ...
    def create(self, job_id, employee_id, message) -> dict: ...
    def find_by_employee(self, employee_id) -> list: ...
    def find_by_employer(self, employer_id) -> list: ...
    def update_status(self, application_id, employer_id, status) -> bool: ...
    def delete(self, application_id, employee_id) -> bool: ...
    # No tiene find_jobs() ni find_users() — esa es responsabilidad de otros repos
```

---

## OCP — Open/Closed Principle

`CompositeMatchingStrategy` puede recibir cualquier instancia de `MatchingStrategy`. Para agregar experiencia como quinto criterio, basta crear `ExperienceMatchStrategy(MatchingStrategy)` y agregarlo a `_strategies` en el constructor.

```python
# OCP: agregar ExperienceMatchStrategy no modifica ninguna clase existente
class ExperienceMatchStrategy(MatchingStrategy):
    @property
    def name(self) -> str:
        return "experience"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        user_exp = user_profile.get("years_exp") or 0
        job_exp  = job.get("min_years_exp") or 0
        if user_exp >= job_exp:
            return 25.0, f"OK:Experiencia: {user_exp} años (mínimo {job_exp})"
        return 0.0, f"NO:Experiencia: tienes {user_exp} años, se requieren {job_exp}"
```

---

## LSP — Liskov Substitution Principle

Las 4 estrategias concretas son sustituibles entre sí. `CompositeMatchingStrategy` las trata como `MatchingStrategy` sin distinguir el tipo concreto.

```python
# LSP: el loop no sabe si la estrategia es City, Modality, Salary o Skills
for strategy in self._strategies:
    pts, msg = strategy.calculate(user_profile, job)
    total += pts
    parts.append(msg)
```

---

## ISP — Interface Segregation Principle

```python
# ISP: interfaz mínima, solo lo necesario
class MatchingStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass

    @abstractmethod
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]: pass
    # No hay save(), serialize(), configure() — cada estrategia no los necesita
```

---

## DIP — Dependency Inversion Principle

```python
# DIP: ApplicationsRouter depende de ApplicationRepository (abstracción), no de SQL directo
@router.post("/")
def apply_to_job(data: ApplyData, current_user=Depends(get_current_user), db=Depends(get_db)):
    repo = ApplicationRepository(db)           # abstracción
    if repo.already_applied(data.job_id, current_user["id"]):
        raise HTTPException(400, "Ya te postulaste a esta vacante")
    app = repo.create(data.job_id, current_user["id"], data.message)
    return {"message": "Postulación enviada", "application_id": app["id"]}
```
