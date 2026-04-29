from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.deps import get_db
from app.security import hash_password, verify_password, create_token
# SOLID: Dependency Inversion - el router depende de la abstracción UserRepository, no de SQL directo
from app.repositories.user_repository import UserRepository

# SOLID: Single Responsibility - este router solo gestiona autenticación (login/registro)
router = APIRouter(prefix="/auth", tags=["Auth"])


class RegisterData(BaseModel):
    email: str
    full_name: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(data: RegisterData, db: Session = Depends(get_db)):
    # GRASP: Controlador - delega la persistencia al UserRepository
    user_repo = UserRepository(db)

    if user_repo.email_exists(data.email):
        raise HTTPException(status_code=400, detail="El email ya esta registrado")

    hashed = hash_password(data.password)
    user = user_repo.create(data.email, data.full_name, hashed)
    token = create_token(user["id"])
    return {"token": token, "user": {"id": user["id"], "email": user["email"], "full_name": user["full_name"]}}


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = user_repo.find_by_email(data.email)

    if not user or not verify_password(data.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_token(user["id"])
    return {"token": token, "user": {"id": user["id"], "email": user["email"], "full_name": user["full_name"]}}
