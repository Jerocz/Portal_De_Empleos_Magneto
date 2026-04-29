# Entrega 3 — Portal de Empleos Magneto
## Ingeniería de Software · Universidad EAFIT

---

## 1. Introducción

El Portal de Empleos Magneto es una aplicación web full-stack que automatiza la búsqueda de empleo mediante un motor de matching inteligente, inspirado en la plataforma colombiana Magneto. La aplicación conecta candidatos con ofertas laborales calculando un score de compatibilidad ponderado que considera tres dimensiones: coincidencia de habilidades técnicas (60% del peso), compatibilidad salarial (25%) y modalidad de trabajo (15%). El sistema permite al candidato registrar su perfil con sus skills, explorar ofertas disponibles y ejecutar el matching con un solo clic, recibiendo notificaciones automáticas de las oportunidades con mayor afinidad.

Desde el punto de vista de ingeniería de software, el proyecto implementa una arquitectura en capas con separación explícita de responsabilidades. El backend está desarrollado en Python con FastAPI y accede a una base de datos MySQL a través de SQLAlchemy. El frontend es una SPA (Single Page Application) construida con HTML5, CSS3 y JavaScript vanilla, que se comunica con la API mediante tokens JWT. A lo largo del desarrollo se aplicaron de forma deliberada los principios SOLID, los patrones GRASP y tres patrones de diseño GoF: Strategy, Repository y Factory, con el objetivo de construir un sistema mantenible, extensible y con bajo acoplamiento entre sus componentes.

---

## 2. Tabla Resumen de Arquitectura

| Atributo | Detalle |
|---|---|
| Tipo de aplicación | Aplicación web full-stack (SPA + REST API) |
| Estilo arquitectónico | Arquitectura en capas (Presentation → Router → Service → Repository → Database) |
| Lenguaje backend | Python 3.11+ |
| Lenguaje frontend | HTML5 / CSS3 / JavaScript ES2022 (vanilla) |
| Framework backend | FastAPI 0.110+ |
| ORM / Base de datos | SQLAlchemy 2.x + MySQL 8.x (driver PyMySQL) |
| Autenticación | JWT (PyJWT, HS256, 24h) + bcrypt (password hashing) |
| Patrones de diseño | Strategy, Repository, Factory (Method) |
| Principios aplicados | SOLID (5 principios), GRASP (9 patrones) |
| Despliegue | Servidor único: Uvicorn sirve la API en :8000 y los archivos estáticos del frontend |

---

## 3. Análisis SOLID

### Tabla de Principios SOLID

| Principio | Sigla | Aplicación en el Proyecto | Archivo(s) Clave |
|---|---|---|---|
| Single Responsibility | SRP | Cada clase tiene una única razón para cambiar: `UserRepository` solo accede a `users`, `SkillMatchingStrategy` solo calcula score de skills, `DTOFactory` solo construye DTOs | `repositories/`, `matching/strategies.py`, `factories/dto_factory.py` |
| Open/Closed | OCP | `CompositeMatchingStrategy` acepta nuevas estrategias sin modificarse. Para añadir una nueva dimensión de matching basta con crear una subclase de `MatchingStrategy` | `matching/strategies.py` |
| Liskov Substitution | LSP | `SkillMatchingStrategy`, `SalaryMatchingStrategy` y `ModalityMatchingStrategy` son intercambiables en `CompositeMatchingStrategy` sin alterar su comportamiento | `matching/strategies.py` |
| Interface Segregation | ISP | `MatchingStrategy` define solo `name` y `calculate()`. No hay métodos de persistencia ni serialización que las estrategias no necesiten | `matching/strategies.py` |
| Dependency Inversion | DIP | Los routers dependen de `Repository` (abstracción) y no de `db.execute(text(...))` de SQLAlchemy directamente | `routers/*.py`, `repositories/*.py` |

### Snippet SRP

```python
# UserRepository: única responsabilidad = acceso a datos de usuarios
class UserRepository:
    def find_by_id(self, user_id: int) -> dict | None: ...
    def find_by_email(self, email: str) -> dict | None: ...
    def email_exists(self, email: str) -> bool: ...
    def create(self, email, full_name, password_hash) -> dict: ...
```

### Snippet OCP

```python
# Agregar ExperienceMatchingStrategy NO modifica CompositeMatchingStrategy
class ExperienceMatchingStrategy(MatchingStrategy):
    def calculate(self, user_profile, job) -> tuple[float, str]:
        user_exp = user_profile.get("years_exp") or 0
        job_exp = job.get("min_years_exp") or 0
        if user_exp >= job_exp:
            return 100.0, f"Experiencia suficiente: {user_exp}/{job_exp} años"
        return round((user_exp / job_exp) * 100, 2), "Experiencia insuficiente"

# Uso: solo se inyecta la nueva estrategia
strategy = CompositeMatchingStrategy(strategies=[
    (SkillMatchingStrategy(), 0.50),
    (SalaryMatchingStrategy(), 0.20),
    (ModalityMatchingStrategy(), 0.15),
    (ExperienceMatchingStrategy(), 0.15),
])
```

### Snippet DIP

```python
# ANTES (acoplamiento alto): el router ejecutaba SQL directamente
# jobs = db.execute(text("SELECT * FROM jobs ...")).fetchall()

# DESPUÉS (DIP aplicado): el router depende del Repository (abstracción)
@router.get("/")
def list_jobs(city=None, modality=None, db=Depends(get_db), ...):
    job_repo = JobRepository(db)
    jobs = job_repo.find_all(city=city, modality=modality)
    return [DTOFactory.job_dto_to_dict(DTOFactory.create_job_dto(j)) for j in jobs]
```

---

## 4. Análisis GRASP

### Tabla de Patrones GRASP

| Patrón GRASP | Aplicación en el Proyecto | Clase(s) Involucradas |
|---|---|---|
| Experto en Información | `SkillMatchingStrategy` calcula score de skills porque tiene toda la información necesaria | `SkillMatchingStrategy`, `SalaryMatchingStrategy`, `ModalityMatchingStrategy` |
| Creador | `DTOFactory` crea `UserProfileDTO`, `JobDTO` y `MatchResultDTO` porque contiene los datos de inicialización | `DTOFactory` |
| Controlador | Los routers de FastAPI reciben eventos HTTP y delegan la lógica a servicios/repositorios | `matching.py`, `jobs.py`, `auth.py` |
| Bajo Acoplamiento | Los routers no conocen SQL; solo interactúan con Repositories y DTOFactory | Todos los `routers/` |
| Alta Cohesión | `MatchRepository` solo tiene operaciones sobre `job_matches`; no mezcla responsabilidades | `MatchRepository`, `JobRepository`, `UserRepository` |
| Polimorfismo | `CompositeMatchingStrategy` llama a `strategy.calculate()` sin distinguir qué estrategia es | `CompositeMatchingStrategy` → `MatchingStrategy` |
| Fabricación Pura | `DTOFactory` y `MatchingService` no corresponden a entidades del dominio real; existen para desacoplar capas | `DTOFactory`, `MatchingService` |
| Indirección | `MatchingService` es intermediario entre el router y las estrategias; los Repositories son intermediarios entre los routers y SQLAlchemy | `MatchingService`, `JobRepository` |
| Variaciones Protegidas | `MatchingStrategy` es la interfaz estable que protege al sistema de cambios en el algoritmo de matching | `MatchingStrategy`, `CompositeMatchingStrategy` |

### Snippet — Polimorfismo

```python
# Sin polimorfismo (mala práctica):
# if isinstance(strategy, SkillMatchingStrategy):
#     score = calcular_skills(...)
# elif isinstance(strategy, SalaryMatchingStrategy):
#     score = calcular_salario(...)

# Con polimorfismo GRASP (implementación real del proyecto):
for strategy, weight in self._strategies:
    score, msg = strategy.calculate(user_profile, job)  # polimórfico
    weighted_score += score * (weight / total_weight)
```

---

## 5. Patrones de Diseño — Tablas Detalladas

---

### PATRÓN 1: Strategy

| Campo | Descripción |
|---|---|
| **Nombre** | Strategy (Estrategia) |
| **Clasificación** | Comportamiento (Behavioral) |
| **Intención** | Definir una familia de algoritmos, encapsular cada uno y hacerlos intercambiables. Permite que el algoritmo varíe independientemente de los clientes que lo usan. |
| **Aplicabilidad** | Se usa cuando: (1) se necesitan variantes de un algoritmo; (2) se quiere evitar condicionales if/elif para seleccionar comportamiento; (3) diferentes clientes necesitan diferentes comportamientos; (4) el algoritmo puede cambiar en tiempo de ejecución. |
| **Estructura** | `Context` → `Strategy` (interfaz abstracta) ← implementaciones concretas |
| **Participantes** | `MatchingStrategy` (Strategy abstracto), `SkillMatchingStrategy` / `SalaryMatchingStrategy` / `ModalityMatchingStrategy` (ConcreteStrategy), `CompositeMatchingStrategy` (Context), `MatchingService` (cliente) |
| **Colaboraciones** | `CompositeMatchingStrategy` delega el cálculo a cada `MatchingStrategy` concreta y combina los resultados ponderados |
| **Consecuencias** | (+) El algoritmo de matching es extensible sin modificar código existente. (+) Se eliminan condicionales en el motor de matching. (-) Incrementa el número de clases en el sistema. |
| **Implementación** | Se define la ABC `MatchingStrategy` con `calculate()`. Cada estrategia implementa su lógica. `CompositeMatchingStrategy` recibe la lista de estrategias+pesos y calcula el score ponderado. |
| **Código de ejemplo** | Ver snippet abajo |
| **Usos conocidos** | Java `Comparator`, Python `key=` en `sorted()`, algoritmos de ordenamiento intercambiables, políticas de caché |
| **Patrones relacionados** | Template Method (similar pero con herencia), Factory Method (puede crear las estrategias), Decorator (puede añadir comportamiento a las estrategias) |

```python
# Strategy abstracto
class MatchingStrategy(ABC):
    @abstractmethod
    def calculate(self, user_profile: dict, job: dict) -> tuple[float, str]:
        pass

# Concrete Strategy 1
class SkillMatchingStrategy(MatchingStrategy):
    def calculate(self, user_profile, job):
        user_set = {s.lower() for s in user_profile.get("skills", [])}
        job_set  = {s.lower() for s in job.get("skills_required", [])}
        score = len(user_set & job_set) / len(job_set) * 100 if job_set else 0
        return round(score, 2), f"Skills: {len(user_set & job_set)}/{len(job_set)} coincidencias"

# Context — combina estrategias con pesos
class CompositeMatchingStrategy:
    def __init__(self, strategies=None):
        self._strategies = strategies or [
            (SkillMatchingStrategy(),    0.60),
            (SalaryMatchingStrategy(),   0.25),
            (ModalityMatchingStrategy(), 0.15),
        ]

    def calculate(self, user_profile, job):
        total = sum(w for _, w in self._strategies)
        score = sum(s.calculate(user_profile, job)[0] * (w / total)
                    for s, w in self._strategies)
        return round(score, 2), "Score ponderado calculado"
```

---

### PATRÓN 2: Repository

| Campo | Descripción |
|---|---|
| **Nombre** | Repository (Repositorio) |
| **Clasificación** | Arquitectural / Acceso a Datos |
| **Intención** | Encapsular la lógica de acceso a datos detrás de una interfaz orientada a colecciones, desacoplando el dominio de la capa de persistencia. |
| **Aplicabilidad** | Se usa cuando: (1) se quiere aislar la lógica de negocio del acceso a base de datos; (2) se necesita intercambiar la fuente de datos sin afectar la lógica de negocio; (3) se quieren testeabilidad y mantenibilidad altas. |
| **Estructura** | `Router/Service` → `Repository` (interfaz) ← implementación concreta con ORM/SQL |
| **Participantes** | `UserRepository`, `JobRepository`, `MatchRepository`, `ProfileRepository` (Concrete Repositories), `Session` de SQLAlchemy (Data Source) |
| **Colaboraciones** | Los routers y servicios solicitan datos a los Repositories; estos ejecutan las queries SQL y retornan diccionarios Python desacoplados del ORM |
| **Consecuencias** | (+) Los routers no conocen SQL ni SQLAlchemy. (+) Cambiar de MySQL a PostgreSQL solo requiere modificar los Repositories. (-) Añade una capa de indirección y más archivos. |
| **Implementación** | Cada Repository recibe una `Session` en su constructor y expone métodos de dominio (`find_by_id`, `create`, `upsert`). Internamente usa `text()` de SQLAlchemy para queries SQL. |
| **Código de ejemplo** | Ver snippet abajo |
| **Usos conocidos** | Spring Data Repository, Django ORM Manager, Entity Framework DbContext, Laravel Eloquent |
| **Patrones relacionados** | Unit of Work (complementa Repository para transacciones), Factory (puede crear Repositories), Data Mapper |

```python
class JobRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_all(self, city=None, modality=None, limit=50) -> list[dict]:
        query = "SELECT * FROM jobs WHERE 1=1"
        params = {}
        if city:
            query += " AND city LIKE :city"
            params["city"] = f"%{city}%"
        if modality:
            query += " AND modality = :modality"
            params["modality"] = modality
        query += f" ORDER BY posted_at DESC LIMIT {limit}"
        rows = self._db.execute(text(query), params).fetchall()
        return [self._parse_skills(dict(r._mapping)) for r in rows]

    def find_by_id(self, job_id: int) -> dict | None:
        row = self._db.execute(
            text("SELECT * FROM jobs WHERE id = :id"), {"id": job_id}
        ).fetchone()
        return self._parse_skills(dict(row._mapping)) if row else None

    def _parse_skills(self, job: dict) -> dict:
        raw = job.get("skills_required")
        job["skills_required"] = json.loads(raw) if isinstance(raw, str) else (raw or [])
        return job
```

---

### PATRÓN 3: Factory Method (DTOFactory)

| Campo | Descripción |
|---|---|
| **Nombre** | Factory Method (Método de Fábrica) — implementado como Static Factory |
| **Clasificación** | Creacional (Creational) |
| **Intención** | Definir una interfaz para crear objetos, pero permitir que las subclases (o métodos estáticos) decidan qué clase instanciar. Desacopla la creación de objetos de su uso. |
| **Aplicabilidad** | Se usa cuando: (1) el código no debe depender de las clases concretas que crea; (2) la creación de objetos involucra lógica compleja de mapeo/transformación; (3) se quiere centralizar la construcción de DTOs para respuestas de API. |
| **Estructura** | `Creator` (DTOFactory) → métodos factory → `Product` (UserProfileDTO, JobDTO, MatchResultDTO) |
| **Participantes** | `DTOFactory` (Creator con métodos estáticos), `UserProfileDTO` / `JobDTO` / `MatchResultDTO` (Products), routers (clientes que usan los productos) |
| **Colaboraciones** | Los routers llaman a `DTOFactory.create_job_dto(job_dict)` para obtener un DTO y luego `DTOFactory.job_dto_to_dict(dto)` para serializarlo a JSON |
| **Consecuencias** | (+) Los routers no construyen dicts de respuesta manualmente. (+) La estructura de respuesta está centralizada. (+) Facilita el testing. (-) Más indirección para respuestas simples. |
| **Implementación** | `DTOFactory` usa `@staticmethod` en cada método factory. Los DTOs son `@dataclass` de Python para inmutabilidad y claridad. |
| **Código de ejemplo** | Ver snippet abajo |
| **Usos conocidos** | `datetime.fromisoformat()`, `Decimal.from_float()`, `Path.from_uri()`, `requests.Response`, serializers de Django REST Framework |
| **Patrones relacionados** | Abstract Factory (fábricas de familias de objetos), Builder (para objetos más complejos), Prototype |

```python
@dataclass
class JobDTO:
    id: int
    title: str
    company: str
    city: str
    modality: str
    salary_min_cop: Optional[int]
    salary_max_cop: Optional[int]
    skills_required: list[str]
    description: Optional[str] = None

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
            description=job.get("description"),
        )

    @staticmethod
    def job_dto_to_dict(dto: JobDTO) -> dict:
        return {
            "id": dto.id, "title": dto.title, "company": dto.company,
            "city": dto.city, "modality": dto.modality,
            "salary_min_cop": dto.salary_min_cop,
            "salary_max_cop": dto.salary_max_cop,
            "skills_required": dto.skills_required,
        }

# Uso en el router (cliente):
@router.get("/")
def list_jobs(...):
    job_repo = JobRepository(db)
    jobs = job_repo.find_all(city=city, modality=modality)
    return [DTOFactory.job_dto_to_dict(DTOFactory.create_job_dto(j)) for j in jobs]
```

---

### PATRÓN 4: Decorator (FastAPI Dependency Injection)

| Campo | Descripción |
|---|---|
| **Nombre** | Decorator (Decorador) — implementado via Dependency Injection de FastAPI |
| **Clasificación** | Estructural (Structural) |
| **Intención** | Añadir responsabilidades adicionales a un objeto (o función) de forma dinámica, sin modificar su estructura. Los decoradores proporcionan una alternativa flexible a la herencia para extender funcionalidad. |
| **Aplicabilidad** | Se usa cuando: (1) se quiere añadir funcionalidad a funciones individuales sin modificarlas; (2) la herencia es impráctica por la cantidad de combinaciones posibles; (3) se necesita autenticación, logging o validación transversal. |
| **Estructura** | `Component` (función endpoint) ← `Decorator` (dependencia inyectada con `Depends()`) |
| **Participantes** | Los endpoints de los routers (Component), `get_current_user` / `get_db` (ConcreteDecorators), FastAPI `Depends()` (mecanismo de inyección) |
| **Colaboraciones** | FastAPI ejecuta las dependencias (`Depends()`) antes del endpoint, inyecta sus resultados y reutiliza las instancias dentro del mismo request (scoped dependencies) |
| **Consecuencias** | (+) La autenticación JWT y la sesión de BD se añaden a cualquier endpoint con una línea. (+) Los endpoints son testables de forma independiente. (-) El orden de ejecución de dependencias puede no ser obvio para principiantes. |
| **Implementación** | `get_db()` usa el patrón `yield` para gestionar el ciclo de vida de la sesión. `get_current_user()` valida el JWT y retorna el usuario autenticado. Ambos se inyectan con `Depends()`. |
| **Código de ejemplo** | Ver snippet abajo |
| **Usos conocidos** | Python `@functools.wraps`, Java `BufferedReader(FileReader(...))`, middleware de Express.js, interceptors de Angular |
| **Patrones relacionados** | Chain of Responsibility (similar pero pasa la responsabilidad), Proxy (similar pero controla el acceso), Strategy (intercambia algoritmos, Decorator añade comportamiento) |

```python
# ConcreteDecorator 1: gestión del ciclo de vida de la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db       # Inyecta la sesión; la cierra automáticamente al terminar
    finally:
        db.close()

# ConcreteDecorator 2: autenticación JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = int(payload["sub"])
    user = db.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id}).fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return dict(user._mapping)

# Aplicación del Decorator: el endpoint recibe autenticación + BD sin implementarlas
@router.get("/")
def get_my_matches(
    current_user: dict = Depends(get_current_user),  # Decorator: inyecta usuario autenticado
    db: Session = Depends(get_db),                    # Decorator: inyecta sesión de BD
):
    match_repo = MatchRepository(db)
    return [DTOFactory.match_dto_to_dict(DTOFactory.create_match_result_dto(m))
            for m in match_repo.find_by_user(current_user["id"])]
```

---

## 6. Conclusiones y Lecciones Aprendidas

La implementación del Portal de Empleos Magneto demostró que la aplicación deliberada de principios SOLID y patrones de diseño transforma un prototipo funcional en un sistema mantenible. La refactorización hacia el patrón Strategy en el motor de matching fue el cambio de mayor impacto: el algoritmo original era una función monolítica `calcular_score()` que solo evaluaba skills. Al convertirlo en tres estrategias ponderadas (skills, salario, modalidad), el sistema pasó de producir scores binarios a generar rankings más realistas que reflejan mejor la compatibilidad real entre candidatos y empleos. Además, agregar una cuarta dimensión de matching (p. ej., años de experiencia) ahora requiere crear una nueva clase sin tocar el código existente, lo que valida el principio Open/Closed en la práctica.

El patrón Repository resultó ser la mejora arquitectónica más impactante en términos de mantenibilidad. Antes de su implementación, los routers mezclaban lógica de negocio con consultas SQL crudas, haciendo imposible testearlos de forma aislada. Con los repositories, cada router se redujo a 5-10 líneas de lógica pura, y toda la complejidad de parseo de JSON, construcción de queries dinámicas y deserialización quedó encapsulada en clases con responsabilidad única. Esta separación es especialmente valiosa porque la base de datos (MySQL) es el componente más propenso a cambiar en un proyecto universitario que eventualmente puede migrarse a PostgreSQL o a un servicio cloud.

Finalmente, la combinación de patrones GRASP (especialmente Bajo Acoplamiento e Indirección) con el patrón Factory para DTOs resolvió un problema sutil pero importante: la serialización de respuestas. En el código original, cada router construía sus diccionarios de respuesta de forma ad-hoc, lo que generaba inconsistencias en los nombres de campos entre endpoints. Con `DTOFactory`, existe un único punto de verdad para la estructura de cada respuesta de la API. La lección más valiosa de esta entrega es que los patrones de diseño no son decoración académica: cada uno resolvió un problema concreto de mantenibilidad, extensibilidad o consistencia que habría sido costoso de corregir una vez el proyecto creciera.

---

*Documento generado para Entrega 3 — Ingeniería de Software, Universidad EAFIT.*
