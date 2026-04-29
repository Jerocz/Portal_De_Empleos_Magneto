# Análisis de Principios SOLID — Portal de Empleos Magneto

## Tabla resumen

| Principio | Sigla | Dónde se aplica en el proyecto | Descripción concreta |
|-----------|-------|-------------------------------|----------------------|
| Single Responsibility | SRP | Cada clase tiene una única razón para cambiar | `UserRepository` solo accede a `users`; `SkillMatchingStrategy` solo evalúa skills; `DTOFactory` solo construye DTOs |
| Open/Closed | OCP | Abierto para extensión, cerrado para modificación | `CompositeMatchingStrategy` acepta nuevas estrategias sin modificar su código; se puede agregar `ExperienceMatchingStrategy` sin tocar nada existente |
| Liskov Substitution | LSP | Subclases son intercambiables con su clase base | `SkillMatchingStrategy`, `SalaryMatchingStrategy` y `ModalityMatchingStrategy` son intercambiables en `CompositeMatchingStrategy.calculate()` |
| Interface Segregation | ISP | Interfaces pequeñas y específicas | `MatchingStrategy` solo define `name` y `calculate()`; no fuerza implementar métodos innecesarios |
| Dependency Inversion | DIP | Módulos de alto nivel dependen de abstracciones | Los routers dependen de `UserRepository`, `JobRepository`, `MatchRepository` y `DTOFactory`; no de `text(...)` de SQLAlchemy directamente |

---

## SRP — Single Responsibility Principle

> *"Una clase debe tener una, y solo una, razón para cambiar."*

### Dónde se aplica

| Clase / Módulo | Única responsabilidad |
|---|---|
| `UserRepository` | Acceso a datos de la tabla `users` |
| `JobRepository` | Acceso a datos de la tabla `jobs` |
| `MatchRepository` | Acceso a datos de la tabla `job_matches` |
| `ProfileRepository` | Acceso a datos de la tabla `profiles` |
| `SkillMatchingStrategy` | Calcular score por coincidencia de skills |
| `SalaryMatchingStrategy` | Calcular score por rango salarial |
| `ModalityMatchingStrategy` | Calcular score por modalidad de trabajo |
| `MatchingService` | Coordinar la ejecución del matching |
| `DTOFactory` | Construir objetos de respuesta de la API |
| `security.py` | Gestionar JWT y hashing de contraseñas |

### Snippet

```python
# SOLID: Single Responsibility - UserRepository solo gestiona acceso a datos de usuarios
class UserRepository:
    def find_by_id(self, user_id: int) -> dict | None: ...
    def find_by_email(self, email: str) -> dict | None: ...
    def email_exists(self, email: str) -> bool: ...
    def create(self, email: str, full_name: str, password_hash: str) -> dict: ...
```

---

## OCP — Open/Closed Principle

> *"El software debe estar abierto para extensión pero cerrado para modificación."*

### Dónde se aplica

`CompositeMatchingStrategy` puede recibir cualquier lista de estrategias. Para agregar una nueva dimensión de matching (p.ej. experiencia requerida), basta con crear `ExperienceMatchingStrategy(MatchingStrategy)` e inyectarla, sin modificar ninguna clase existente.

### Snippet

```python
# SOLID: Open/Closed - se agrega ExperienceMatchingStrategy sin modificar CompositeMatchingStrategy
class ExperienceMatchingStrategy(MatchingStrategy):
    @property
    def name(self) -> str:
        return "experience"

    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        user_exp = user_profile.get("years_exp") or 0
        job_exp = job.get("min_years_exp") or 0
        if user_exp >= job_exp:
            return 100.0, f"Experiencia: tienes {user_exp} años, se requieren {job_exp}"
        return round((user_exp / job_exp) * 100, 2), f"Experiencia insuficiente: {user_exp}/{job_exp} años"

# Uso sin modificar CompositeMatchingStrategy:
strategy = CompositeMatchingStrategy(strategies=[
    (SkillMatchingStrategy(), 0.50),
    (SalaryMatchingStrategy(), 0.20),
    (ModalityMatchingStrategy(), 0.15),
    (ExperienceMatchingStrategy(), 0.15),   # <-- nueva estrategia agregada
])
```

---

## LSP — Liskov Substitution Principle

> *"Los objetos de una subclase deben poder sustituir a los de la clase padre sin alterar el comportamiento del programa."*

### Dónde se aplica

Todas las estrategias concretas son sustituibles entre sí en `CompositeMatchingStrategy` porque todas implementan el mismo contrato de `MatchingStrategy.calculate()`.

### Snippet

```python
# SOLID: Liskov Substitution - las tres estrategias son intercambiables
def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
    total_weight = sum(w for _, w in self._strategies)
    weighted_score = 0.0
    explanations: list[str] = []

    for strategy, weight in self._strategies:
        # 'strategy' puede ser Skill, Salary o Modality - el código no lo sabe ni le importa
        score, msg = strategy.calculate(user_profile, job)
        weighted_score += score * (weight / total_weight)
        explanations.append(msg)
    ...
```

---

## ISP — Interface Segregation Principle

> *"Los clientes no deben ser forzados a depender de interfaces que no usan."*

### Dónde se aplica

`MatchingStrategy` es una interfaz mínima: solo define `name` (propiedad) y `calculate()` (método). No hay métodos de serialización, persistencia ni configuración que una estrategia no necesite.

### Snippet

```python
# SOLID: Interface Segregation - interfaz mínima, solo lo que necesita cada estrategia
class MatchingStrategy(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        pass
    # No hay save(), serialize(), configure() - cada estrategia no necesita esos métodos
```

---

## DIP — Dependency Inversion Principle

> *"Los módulos de alto nivel no deben depender de módulos de bajo nivel. Ambos deben depender de abstracciones."*

### Dónde se aplica

Los routers (módulos de alto nivel) dependen de `Repository` y `DTOFactory` (abstracciones), no de `db.execute(text(...))` directamente (módulo de bajo nivel = SQLAlchemy + SQL crudo).

### Snippet

```python
# SOLID: Dependency Inversion - el router de matching depende de abstracciones
# (MatchingService, ProfileRepository, MatchRepository, DTOFactory)
# y NO de SQLAlchemy text() directamente

@router.post("/run")
def run_matching(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    profile_repo = ProfileRepository(db)          # abstracción
    service = MatchingService(db)                  # abstracción
    profile = profile_repo.find_by_user_id(current_user["id"])
    nuevos_matches = service.run_matching(current_user["id"], profile)
    return {"message": f"Matching completado. {nuevos_matches} nuevos matches encontrados hoy."}
```
