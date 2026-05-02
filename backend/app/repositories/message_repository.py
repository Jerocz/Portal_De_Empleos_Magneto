from sqlalchemy.orm import Session
from sqlalchemy import text


class MessageRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, application_id: int, sender_id: int, receiver_id: int, content: str) -> dict:
        self._db.execute(
            text("""
                INSERT INTO messages (application_id, sender_id, receiver_id, content)
                VALUES (:app_id, :sender, :receiver, :content)
            """),
            {"app_id": application_id, "sender": sender_id,
             "receiver": receiver_id, "content": content},
        )
        self._db.commit()
        # Obtener el ID del mensaje recién insertado
        row = self._db.execute(text("SELECT LAST_INSERT_ID() AS id")).fetchone()
        if not row or not row.id:
            return {"id": 0, "sent_at": "now"}
        return {
            "id": row.id,
            "application_id": application_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content,
            "sent_at": "now",
        }

    def find_by_application(self, application_id: int) -> list[dict]:
        rows = self._db.execute(
            text("""
                SELECT m.*, u.full_name AS sender_name
                FROM messages m
                JOIN users u ON u.id = m.sender_id
                WHERE m.application_id = :app_id
                ORDER BY m.sent_at ASC
            """),
            {"app_id": application_id},
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r._mapping)
            d["sent_at"] = str(d["sent_at"])
            result.append(d)
        return result

    def find_unread_by_receiver(self, receiver_id: int) -> list[dict]:
        rows = self._db.execute(
            text("""
                SELECT m.id, m.content, m.sent_at, m.application_id,
                       u.full_name AS sender_name,
                       j.title AS job_title
                FROM messages m
                JOIN users u ON u.id = m.sender_id
                JOIN applications a ON a.id = m.application_id
                JOIN jobs j ON j.id = a.job_id
                WHERE m.receiver_id = :rid AND m.is_read = FALSE
                ORDER BY m.sent_at DESC
            """),
            {"rid": receiver_id},
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r._mapping)
            d["sent_at"] = str(d["sent_at"])
            result.append(d)
        return result

    def mark_read(self, application_id: int, receiver_id: int) -> None:
        self._db.execute(
            text("""
                UPDATE messages SET is_read = TRUE
                WHERE application_id = :app_id AND receiver_id = :rid
            """),
            {"app_id": application_id, "rid": receiver_id},
        )
        self._db.commit()
