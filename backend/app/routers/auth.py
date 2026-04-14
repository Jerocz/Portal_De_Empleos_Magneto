from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, EmailStr
from app.deps import get_db
from app.security import hash_password, verify_password, create_token

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
    existing = db.execute(text("SELECT id FROM users WHERE email = :e"), {"e": data.email}).fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya esta registrado")

    hashed = hash_password(data.password)
    db.execute(
        text("INSERT INTO users (email, full_name, password_hash, is_active) VALUES (:e, :n, :p, 1)"),
        {"e": data.email, "n": data.full_name, "p": hashed}
    )
    db.commit()

    user = db.execute(text("SELECT * FROM users WHERE email = :e"), {"e": data.email}).fetchone()
    token = create_token(user.id)
    return {"token": token, "user": {"id": user.id, "email": user.email, "full_name": user.full_name}}


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.execute(text("SELECT * FROM users WHERE email = :e"), {"e": data.email}).fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    user_dict = dict(user._mapping)
    password_hash = user_dict.get("password_hash", "")

    if not password_hash or not verify_password(data.password, password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    token = create_token(user.id)
    return {"token": token, "user": {"id": user.id, "email": user.email, "full_name": user.full_name}}
