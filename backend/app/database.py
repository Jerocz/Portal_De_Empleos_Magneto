import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Variable DATABASE_URL no definida. "
        "Copia .env.example a .env y configura tu conexion MySQL."
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,    # verifica conexion antes de usarla
    pool_recycle=1800,     # reconecta cada 30 min (evita timeouts MySQL)
    connect_args={"connect_timeout": 10},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
