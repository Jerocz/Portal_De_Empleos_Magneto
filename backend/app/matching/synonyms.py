"""
Módulo de sinónimos de habilidades para búsqueda semántica.

Cómo funciona:
- Cada clave es una variante que un usuario podría escribir (normalizada: sin tildes, minúsculas)
- El valor es la forma canónica a la que se mapea
- canonicalize("JS") → "javascript"
- canonicalize("NodeJS") → "javascript"  (Node es parte del ecosistema JS)
- Si la skill no está en el diccionario, se retorna tal cual (normalizada)

Para agregar nuevos sinónimos: añadir entradas al diccionario SYNONYMS.
"""
import unicodedata

# Diccionario de sinónimos: variante → forma canónica
SYNONYMS: dict[str, str] = {
    # JavaScript y ecosistema
    "js":               "javascript",
    "javascript":       "javascript",
    "nodejs":           "javascript",
    "node.js":          "javascript",
    "node":             "javascript",
    "ecmascript":       "javascript",
    "es6":              "javascript",
    "es2015":           "javascript",
    "typescript":       "typescript",
    "ts":               "typescript",

    # Frontend frameworks
    "reactjs":          "react",
    "react.js":         "react",
    "react":            "react",
    "react native":     "react native",
    "vuejs":            "vue",
    "vue.js":           "vue",
    "vue":              "vue",
    "angularjs":        "angular",
    "angular.js":       "angular",
    "angular":          "angular",
    "nextjs":           "next.js",
    "next.js":          "next.js",
    "next":             "next.js",
    "nuxtjs":           "nuxt.js",
    "nuxt":             "nuxt.js",
    "svelte":           "svelte",
    "html5":            "html",
    "html":             "html",
    "css3":             "css",
    "css":              "css",

    # Python y ecosistema
    "py":               "python",
    "python":           "python",
    "python3":          "python",
    "django":           "django",
    "flask":            "flask",
    "fastapi":          "fastapi",
    "pandas":           "pandas",
    "numpy":            "numpy",
    "scikit":           "scikit-learn",
    "sklearn":          "scikit-learn",
    "scikit-learn":     "scikit-learn",
    "tensorflow":       "tensorflow",
    "tf":               "tensorflow",
    "pytorch":          "pytorch",
    "torch":            "pytorch",

    # Java y ecosistema
    "java":             "java",
    "spring":           "spring boot",
    "spring boot":      "spring boot",
    "springboot":       "spring boot",
    "maven":            "maven",
    "gradle":           "gradle",
    "kotlin":           "kotlin",

    # Bases de datos
    "mysql":            "mysql",
    "postgresql":       "postgresql",
    "postgres":         "postgresql",
    "psql":             "postgresql",
    "mongodb":          "mongodb",
    "mongo":            "mongodb",
    "redis":            "redis",
    "sqlite":           "sqlite",
    "sql server":       "sql server",
    "mssql":            "sql server",
    "oracle":           "oracle",
    "sql":              "sql",
    "nosql":            "nosql",
    "firebase":         "firebase",
    "dynamodb":         "dynamodb",
    "cassandra":        "cassandra",
    "elasticsearch":    "elasticsearch",
    "elastic":          "elasticsearch",

    # Cloud y DevOps
    "aws":              "aws",
    "amazon web services": "aws",
    "gcp":              "gcp",
    "google cloud":     "gcp",
    "azure":            "azure",
    "microsoft azure":  "azure",
    "docker":           "docker",
    "kubernetes":       "kubernetes",
    "k8s":              "kubernetes",
    "terraform":        "terraform",
    "ansible":          "ansible",
    "jenkins":          "jenkins",
    "github actions":   "github actions",
    "gitlab ci":        "gitlab ci",
    "ci/cd":            "ci/cd",
    "cicd":             "ci/cd",
    "linux":            "linux",
    "bash":             "bash",
    "shell":            "bash",

    # Otros lenguajes
    "c++":              "c++",
    "cpp":              "c++",
    "c#":               "c#",
    "csharp":           "c#",
    "dotnet":           ".net",
    ".net":             ".net",
    "golang":           "go",
    "go":               "go",
    "ruby":             "ruby",
    "rails":            "ruby on rails",
    "ruby on rails":    "ruby on rails",
    "php":              "php",
    "laravel":          "laravel",
    "swift":            "swift",
    "rust":             "rust",
    "scala":            "scala",
    "r":                "r",

    # Herramientas y metodologías
    "git":              "git",
    "github":           "github",
    "gitlab":           "gitlab",
    "bitbucket":        "bitbucket",
    "scrum":            "scrum",
    "agile":            "agile",
    "jira":             "jira",
    "figma":            "figma",
    "postman":          "postman",
    "graphql":          "graphql",
    "rest":             "rest api",
    "rest api":         "rest api",
    "restful":          "rest api",
    "api rest":         "rest api",
    "microservices":    "microservicios",
    "microservicios":   "microservicios",

    # Datos e IA
    "machine learning": "machine learning",
    "ml":               "machine learning",
    "deep learning":    "deep learning",
    "dl":               "deep learning",
    "inteligencia artificial": "ia",
    "ia":               "ia",
    "ai":               "ia",
    "data science":     "data science",
    "ciencia de datos": "data science",
    "power bi":         "power bi",
    "tableau":          "tableau",
    "excel":            "excel",
}


def _normalize_raw(text: str) -> str:
    """Normaliza sin tildes y en minúsculas."""
    if not text:
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_tildes.lower().strip()


def canonicalize(skill: str) -> str:
    """
    Convierte una skill a su forma canónica.
    Ejemplo: canonicalize("JS") → "javascript"
             canonicalize("Postgres") → "postgresql"
             canonicalize("MiSkillRara") → "myskillrara"  (sin cambio si no está en el dict)
    """
    normalized = _normalize_raw(skill)
    return SYNONYMS.get(normalized, normalized)


def canonicalize_set(skills: list[str]) -> set[str]:
    """Convierte una lista de skills a un conjunto de formas canónicas."""
    return {canonicalize(s) for s in skills if s and s.strip()}
