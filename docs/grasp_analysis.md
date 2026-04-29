# Análisis de Patrones GRASP — Portal de Empleos Magneto

GRASP (General Responsibility Assignment Software Patterns) define 9 principios para asignar
responsabilidades a clases y objetos en diseño orientado a objetos.

---

## 1. Experto en Información (Information Expert)

> *"Asignar la responsabilidad a la clase que tiene la información necesaria para cumplirla."*

### Aplicación en el proyecto

`SkillMatchingStrategy` tiene toda la información necesaria para calcular la coincidencia de
habilidades: sabe cómo normalizar skills (lowercase/strip), cómo calcular intersecciones y cómo
generar la explicación. Por eso es ella quien calcula el score de skills, no el router ni el servicio.

De igual forma, `JobRepository` es experta en cómo leer y parsear registros de `jobs` (incluyendo
deserializar `skills_required` de JSON), y `ProfileRepository` es experta en leer perfiles.

### Snippet

```python
# GRASP: Experto - SkillMatchingStrategy posee todo el conocimiento para calcular coincidencias
class SkillMatchingStrategy(MatchingStrategy):
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        user_set = {s.lower().strip() for s in user_profile.get("skills") or []}
        job_set  = {s.lower().strip() for s in job.get("skills_required") or []}
        coincidencias = user_set & job_set
        score = round(len(coincidencias) / len(job_set) * 100, 2)
        ...
```

---

## 2. Creador (Creator)

> *"Asignar a la clase B la responsabilidad de crear instancias de A si: B contiene A, B agrega A,
> B usa A de manera cercana, o B tiene los datos de inicialización de A."*

### Aplicación en el proyecto

`DTOFactory` es la Creadora de `UserProfileDTO`, `JobDTO` y `MatchResultDTO`. Tiene los datos de
inicialización (los dicts de la base de datos) y conoce cómo mapearlos a los DTOs. Los routers
no crean DTOs directamente; se los delegan a la Factory.

`CompositeMatchingStrategy` crea las instancias de `SkillMatchingStrategy`, `SalaryMatchingStrategy`
y `ModalityMatchingStrategy` cuando se instancia con la configuración por defecto, porque es quien
conoce cómo deben combinarse.

### Snippet

```python
# GRASP: Creador - DTOFactory crea JobDTO porque tiene todos sus datos de inicialización
class DTOFactory:
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
        )
```

---

## 3. Controlador (Controller)

> *"Asignar la responsabilidad de manejar los eventos del sistema a una clase que representa
> el sistema completo o un caso de uso."*

### Aplicación en el proyecto

Los **routers de FastAPI** (`auth.py`, `matching.py`, `jobs.py`, etc.) actúan como Controladores:
reciben las peticiones HTTP, validan la autenticación y delegan la lógica de negocio a los
servicios y repositorios. No contienen SQL ni lógica de negocio.

`MatchingService` es un Controlador de caso de uso: orquesta la interacción entre `JobRepository`,
`MatchRepository` y `CompositeMatchingStrategy` para ejecutar el matching completo.

### Snippet

```python
# GRASP: Controlador - el router delega la lógica al servicio
@router.post("/run")
def run_matching(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    profile_repo = ProfileRepository(db)
    service = MatchingService(db)                    # Controlador de caso de uso
    profile = profile_repo.find_by_user_id(current_user["id"])
    nuevos_matches = service.run_matching(current_user["id"], profile)
    return {"message": f"Matching completado. {nuevos_matches} nuevos matches encontrados hoy."}
```

---

## 4. Bajo Acoplamiento (Low Coupling)

> *"Asignar responsabilidades para minimizar las dependencias entre clases."*

### Aplicación en el proyecto

Los routers no dependen de SQLAlchemy directamente; solo dependen de las interfaces de los
Repositories. Si se cambia MySQL por PostgreSQL, solo cambian los Repositories; los routers
permanecen sin cambios.

`MatchingService` no depende de ningún router; solo de `JobRepository`, `MatchRepository` y
`CompositeMatchingStrategy`. Estas dependencias son inyectadas, no instanciadas internamente.

### Snippet

```python
# GRASP: Bajo Acoplamiento - notifications.py no conoce SQL; solo usa MatchRepository
@router.get("/")
def get_notifications(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    match_repo = MatchRepository(db)
    rows = match_repo.find_notifications(current_user["id"], SCORE_MINIMO)
    # Si cambia la BD o el ORM, solo cambia MatchRepository, no este archivo
    notificaciones = [{"titulo": f"Match con {n['title']}...", ...} for n in rows]
    return {"total": len(notificaciones), "notificaciones": notificaciones}
```

---

## 5. Alta Cohesión (High Cohesion)

> *"Asignar responsabilidades para que la cohesión de una clase siga siendo alta;
> usar esto para evaluar las alternativas."*

### Aplicación en el proyecto

`MatchRepository` contiene únicamente métodos relacionados con `job_matches`:
`find_by_user`, `find_by_user_job_date`, `create`, `find_notifications`. No tiene métodos de
usuarios ni de empleos.

`SkillMatchingStrategy` solo calcula el score de skills; no serializa, no accede a BD, no construye
respuestas HTTP.

### Snippet

```python
# GRASP: Alta Cohesión - MatchRepository solo tiene operaciones de job_matches
class MatchRepository:
    def find_by_user(self, user_id, limit=20) -> list[dict]: ...
    def find_by_user_job_date(self, user_id, job_id, run_date) -> dict | None: ...
    def create(self, user_id, job_id, score, explanation, run_date) -> None: ...
    def find_notifications(self, user_id, min_score, limit=10) -> list[dict]: ...
    # No hay find_user() ni find_jobs() aquí - esa es responsabilidad de otros repositorios
```

---

## 6. Polimorfismo (Polymorphism)

> *"Cuando los comportamientos alternativos varían según el tipo, usar operaciones polimórficas
> en lugar de condicionales."*

### Aplicación en el proyecto

`CompositeMatchingStrategy` llama a `strategy.calculate()` para cada estrategia. El sistema no
necesita `if strategy == "skills": ...` ni `elif strategy == "salary": ...`. Cada clase sabe
cómo calcular su propio score. Agregar una nueva dimensión es agregar una clase, no un `elif`.

### Snippet

```python
# GRASP: Polimorfismo - no hay if/elif para distinguir estrategias, cada una calcula su propio score
for strategy, weight in self._strategies:
    score, msg = strategy.calculate(user_profile, job)   # Polimorfismo en acción
    weighted_score += score * (weight / total_weight)
    explanations.append(msg)

# Comparar con la versión SIN polimorfismo (mala práctica):
# if isinstance(strategy, SkillMatchingStrategy):
#     score = calcular_skills(...)
# elif isinstance(strategy, SalaryMatchingStrategy):
#     score = calcular_salario(...)
```

---

## 7. Fabricación Pura (Pure Fabrication)

> *"Asignar responsabilidades a una clase artificial (no del dominio real) cuando ninguna clase
> del dominio es una buena candidata para la responsabilidad."*

### Aplicación en el proyecto

`DTOFactory` no corresponde a ninguna entidad del negocio (no es un User, ni un Job, ni un Match).
Es una fabricación pura: existe exclusivamente para desacoplar la transformación de datos de base
de datos en objetos de respuesta HTTP.

`MatchingService` también es una fabricación pura: el dominio real no tiene un objeto "servicio de
matching"; es una abstracción creada para separar la orquestación del matching de los routers.

### Snippet

```python
# GRASP: Fabricación Pura - DTOFactory no existe en el dominio real del negocio
# No es un User, ni un Job, ni un Match; existe solo para desacoplar capas
class DTOFactory:
    @staticmethod
    def create_match_result_dto(match: dict) -> MatchResultDTO:
        return MatchResultDTO(
            id=match["id"],
            job_id=match["job_id"],
            score=float(match["score"]),
            explanation=match.get("explanation", ""),
            ...
        )
```

---

## 8. Indirección (Indirection)

> *"Para evitar el acoplamiento directo entre dos elementos, asignar la responsabilidad a un
> objeto intermediario."*

### Aplicación en el proyecto

`MatchingService` actúa como intermediario entre el router `/matches/run` y las estrategias
concretas. El router no llama directamente a `SkillMatchingStrategy.calculate()`; pasa por el
servicio que gestiona la orquestación.

Los Repositories son intermediarios entre los routers y SQLAlchemy/MySQL: los routers nunca
ejecutan `db.execute(text(...))` directamente.

### Snippet

```python
# GRASP: Indirección - MatchingService es el intermediario entre el router y las Strategies
class MatchingService:
    def run_matching(self, user_id: int, user_profile: dict) -> int:
        jobs = self._job_repo.find_all(limit=200)       # Indirección a BD
        for job in jobs:
            score, explanation = self._strategy.calculate(user_profile, job)  # Indirección a Strategy
            if score > 0:
                self._match_repo.create(user_id, job["id"], score, explanation, date.today())
        self._db.commit()
        return nuevos_matches

# El router solo ve esto:
service = MatchingService(db)
nuevos_matches = service.run_matching(current_user["id"], profile)
```

---

## 9. Variaciones Protegidas (Protected Variations)

> *"Identificar los puntos de variación o inestabilidad y asignar responsabilidades para crear
> una interfaz estable alrededor de ellos."*

### Aplicación en el proyecto

El algoritmo de matching es el punto más probable de cambio en el sistema (puede requerir nuevas
dimensiones, pesos diferentes, modelos de ML, etc.). `MatchingStrategy` es la interfaz estable que
protege al resto del sistema de esos cambios.

Si mañana se reemplaza el cálculo de skills por un modelo de NLP, solo cambia
`SkillMatchingStrategy`; el router, el servicio y las otras estrategias no se tocan.

### Snippet

```python
# GRASP: Variaciones Protegidas - la interfaz MatchingStrategy protege al sistema de cambios en el algoritmo
class MatchingStrategy(ABC):
    @abstractmethod
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        pass  # Todo lo que está detrás de esta interfaz puede cambiar libremente

# CompositeMatchingStrategy está protegida: no importa cómo cambie SkillMatchingStrategy
class CompositeMatchingStrategy:
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        for strategy, weight in self._strategies:
            score, msg = strategy.calculate(user_profile, job)  # Punto de variación protegido
            ...
```
