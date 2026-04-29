"""
Script de seed para datos de demostración.
Inserta 5 usuarios y 10 empleos en MySQL para demo sin registro manual.

Uso:
    cd Portal_De_Empleos_Magneto
    python scripts/seed_demo.py

Credenciales principales:
    Email:      demo@magneto.co
    Contraseña: demo1234
"""
import sys
import os
import json

# Permite importar desde backend/app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: No se encontró DATABASE_URL en el archivo .env")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ── Datos de usuarios demo ──────────────────────────────────────────────────

USERS = [
    {
        "email": "demo@magneto.co",
        "full_name": "Demo User",
        "password": "demo1234",
        "profile": {
            "skills": ["python", "fastapi", "react", "javascript", "mysql", "git", "docker"],
            "location_city": "Medellín",
            "modality": "remote",
            "salary_min_cop": 4_000_000,
            "salary_max_cop": 7_000_000,
            "years_exp": 3,
        },
    },
    {
        "email": "ana@ejemplo.co",
        "full_name": "Ana García",
        "password": "pass1234",
        "profile": {
            "skills": ["react", "javascript", "css", "html", "typescript", "figma"],
            "location_city": "Bogotá",
            "modality": "hybrid",
            "salary_min_cop": 3_500_000,
            "salary_max_cop": 5_500_000,
            "years_exp": 2,
        },
    },
    {
        "email": "carlos@ejemplo.co",
        "full_name": "Carlos Pérez",
        "password": "pass1234",
        "profile": {
            "skills": ["python", "pandas", "sql", "tableau", "machine learning", "scikit-learn"],
            "location_city": "Medellín",
            "modality": "on-site",
            "salary_min_cop": 5_000_000,
            "salary_max_cop": 8_000_000,
            "years_exp": 4,
        },
    },
    {
        "email": "lucia@ejemplo.co",
        "full_name": "Lucía Martínez",
        "password": "pass1234",
        "profile": {
            "skills": ["java", "spring boot", "postgresql", "docker", "kubernetes", "microservices"],
            "location_city": "Cali",
            "modality": "remote",
            "salary_min_cop": 6_000_000,
            "salary_max_cop": 10_000_000,
            "years_exp": 5,
        },
    },
    {
        "email": "david@ejemplo.co",
        "full_name": "David Rodríguez",
        "password": "pass1234",
        "profile": {
            "skills": ["docker", "kubernetes", "aws", "terraform", "linux", "ci/cd"],
            "location_city": "Bogotá",
            "modality": "hybrid",
            "salary_min_cop": 7_000_000,
            "salary_max_cop": 12_000_000,
            "years_exp": 6,
        },
    },
]

# ── Datos de empleos demo ───────────────────────────────────────────────────

JOBS = [
    {
        "title": "Desarrollador Full Stack Python/React",
        "company": "TechColombia S.A.S",
        "city": "Medellín",
        "modality": "remote",
        "description": "Buscamos desarrollador full stack con experiencia en Python y React para proyectos de transformación digital.",
        "salary_min_cop": 5_000_000,
        "salary_max_cop": 8_000_000,
        "skills_required": ["python", "react", "javascript", "git", "mysql", "fastapi"],
    },
    {
        "title": "Frontend Developer React",
        "company": "Innovasoft",
        "city": "Bogotá",
        "modality": "hybrid",
        "description": "Desarrollador frontend con dominio de React y TypeScript para proyectos de e-commerce.",
        "salary_min_cop": 4_000_000,
        "salary_max_cop": 6_000_000,
        "skills_required": ["react", "javascript", "typescript", "css", "html"],
    },
    {
        "title": "Data Scientist Jr",
        "company": "DataMinds Colombia",
        "city": "Medellín",
        "modality": "on-site",
        "description": "Científico de datos para proyectos de machine learning en retail.",
        "salary_min_cop": 4_500_000,
        "salary_max_cop": 7_000_000,
        "skills_required": ["python", "pandas", "sql", "machine learning", "tableau"],
    },
    {
        "title": "Backend Java Developer",
        "company": "Bancolombia Digital",
        "city": "Medellín",
        "modality": "hybrid",
        "description": "Desarrollador backend Java para plataforma de servicios financieros digitales.",
        "salary_min_cop": 6_000_000,
        "salary_max_cop": 9_000_000,
        "skills_required": ["java", "spring boot", "postgresql", "docker", "microservices"],
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudCo",
        "city": "Bogotá",
        "modality": "remote",
        "description": "Ingeniero DevOps con experiencia en cloud AWS y contenedores para infraestructura crítica.",
        "salary_min_cop": 8_000_000,
        "salary_max_cop": 14_000_000,
        "skills_required": ["docker", "kubernetes", "aws", "terraform", "linux", "ci/cd"],
    },
    {
        "title": "Desarrollador Backend Python",
        "company": "Rappi Tech",
        "city": "Bogotá",
        "modality": "hybrid",
        "description": "Backend developer para el equipo de plataforma de pagos y logística.",
        "salary_min_cop": 5_500_000,
        "salary_max_cop": 9_000_000,
        "skills_required": ["python", "fastapi", "mysql", "docker", "git"],
    },
    {
        "title": "Frontend Angular Developer",
        "company": "Pragma S.A",
        "city": "Medellín",
        "modality": "on-site",
        "description": "Desarrollador frontend Angular para proyectos bancarios de alta disponibilidad.",
        "salary_min_cop": 4_000_000,
        "salary_max_cop": 6_500_000,
        "skills_required": ["angular", "javascript", "typescript", "css", "html"],
    },
    {
        "title": "Analista de Datos SQL",
        "company": "Grupo Éxito Digital",
        "city": "Envigado",
        "modality": "hybrid",
        "description": "Análisis de datos de retail y generación de reportes ejecutivos.",
        "salary_min_cop": 3_500_000,
        "salary_max_cop": 5_500_000,
        "skills_required": ["sql", "tableau", "python", "pandas"],
    },
    {
        "title": "Arquitecto de Software Cloud",
        "company": "PSL S.A",
        "city": "Medellín",
        "modality": "remote",
        "description": "Arquitecto de software para liderar proyectos de transformación digital en la nube.",
        "salary_min_cop": 10_000_000,
        "salary_max_cop": 16_000_000,
        "skills_required": ["python", "java", "docker", "kubernetes", "aws", "postgresql"],
    },
    {
        "title": "QA Automation Engineer",
        "company": "Globant Colombia",
        "city": "Bogotá",
        "modality": "remote",
        "description": "Ingeniero de calidad con automatización de pruebas para proyectos de videojuegos y fintech.",
        "salary_min_cop": 4_500_000,
        "salary_max_cop": 7_500_000,
        "skills_required": ["python", "javascript", "git", "docker"],
    },
]


def seed():
    print("=" * 55)
    print("  Portal de Empleos Magneto — Seed de Demo")
    print("=" * 55)

    with Session() as db:
        print("\n[1/4] Limpiando datos previos...")
        db.execute(text("DELETE FROM job_matches WHERE 1=1"))
        db.execute(text("DELETE FROM profiles WHERE 1=1"))
        for user in USERS:
            db.execute(text("DELETE FROM users WHERE email = :e"), {"e": user["email"]})
        db.execute(text("DELETE FROM jobs WHERE 1=1"))
        db.commit()
        print("     ✓ Tablas limpiadas")

        print("\n[2/4] Insertando 10 empleos...")
        for job in JOBS:
            db.execute(
                text("""
                    INSERT INTO jobs
                        (title, company, city, modality, description,
                         salary_min_cop, salary_max_cop, skills_required, posted_at)
                    VALUES
                        (:title, :company, :city, :modality, :desc,
                         :smin, :smax, :skills, NOW())
                """),
                {
                    "title": job["title"],
                    "company": job["company"],
                    "city": job["city"],
                    "modality": job["modality"],
                    "desc": job["description"],
                    "smin": job["salary_min_cop"],
                    "smax": job["salary_max_cop"],
                    "skills": json.dumps(job["skills_required"]),
                },
            )
        db.commit()
        print(f"     ✓ {len(JOBS)} empleos insertados")

        print("\n[3/4] Insertando 5 usuarios y perfiles...")
        for user in USERS:
            db.execute(
                text(
                    "INSERT INTO users (email, full_name, password_hash, is_active) "
                    "VALUES (:e, :n, :p, 1)"
                ),
                {"e": user["email"], "n": user["full_name"], "p": hash_pw(user["password"])},
            )
            db.commit()

            row = db.execute(
                text("SELECT id FROM users WHERE email = :e"), {"e": user["email"]}
            ).fetchone()
            uid = row.id

            p = user["profile"]
            db.execute(
                text("""
                    INSERT INTO profiles
                        (user_id, location_city, modality, salary_min_cop,
                         salary_max_cop, years_exp, skills, updated_at)
                    VALUES (:uid, :city, :mod, :smin, :smax, :yexp, :skills, NOW())
                """),
                {
                    "uid": uid,
                    "city": p["location_city"],
                    "mod": p["modality"],
                    "smin": p["salary_min_cop"],
                    "smax": p["salary_max_cop"],
                    "yexp": p["years_exp"],
                    "skills": json.dumps(p["skills"]),
                },
            )
            db.commit()

        print(f"     ✓ {len(USERS)} usuarios y perfiles insertados")

        print("\n[4/4] Verificando datos...")
        total_jobs = db.execute(text("SELECT COUNT(*) FROM jobs")).scalar()
        total_users = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        print(f"     ✓ Empleos en BD: {total_jobs}")
        print(f"     ✓ Usuarios en BD: {total_users}")

    print("\n" + "=" * 55)
    print("  CREDENCIALES DE ACCESO PARA DEMO")
    print("=" * 55)
    for user in USERS:
        marker = " ← PRINCIPAL" if user["email"] == "demo@magneto.co" else ""
        print(f"  {user['email']:<30} | {user['password']}{marker}")
    print("=" * 55)
    print("\nPasos para la demo:")
    print("  1. Acceder a http://localhost:8000")
    print("  2. Login con demo@magneto.co / demo1234")
    print("  3. Ir a Mi Perfil para ver las skills cargadas")
    print("  4. En el Dashboard, hacer clic en 'Buscar Matches'")
    print("  5. Ver matches ponderados con score por skills, salario y modalidad\n")


if __name__ == "__main__":
    seed()
