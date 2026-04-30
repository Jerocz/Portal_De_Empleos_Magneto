"""
Patrón de Diseño: Repository
Encapsula toda la lógica de acceso a datos de la entidad User.
"""
from sqlalchemy.orm import Session
from sqlalchemy import text


# SOLID: Single Responsibility - solo gestiona acceso a datos de usuarios
# GRASP: Bajo Acoplamiento - el resto del sistema accede a usuarios solo a través de esta clase
class UserRepository:
    """Gestiona el acceso a la tabla `users` en la base de datos."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_id(self, user_id: int) -> dict | None:
        row = self._db.execute(
            text("SELECT * FROM users WHERE id = :id"), {"id": user_id}
        ).fetchone()
        return dict(row._mapping) if row else None

    def find_by_email(self, email: str) -> dict | None:
        row = self._db.execute(
            text("SELECT * FROM users WHERE email = :e"), {"e": email}
        ).fetchone()
        return dict(row._mapping) if row else None

    def email_exists(self, email: str) -> bool:
        row = self._db.execute(
            text("SELECT id FROM users WHERE email = :e"), {"e": email}
        ).fetchone()
        return row is not None

    def create(self, email: str, full_name: str, password_hash: str, role: str = "employee") -> dict:
        self._db.execute(
            text(
                "INSERT INTO users (email, full_name, password_hash, role, is_active) "
                "VALUES (:e, :n, :p, :r, 1)"
            ),
            {"e": email, "n": full_name, "p": password_hash, "r": role},
        )
        self._db.commit()
        return self.find_by_email(email)
