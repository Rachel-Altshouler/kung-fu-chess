from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path


DEFAULT_RATING = 1200


class UserDatabase:
    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parent / "game_data.db"
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    rating INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    #פונקציה חד-כיוונית (SHA-256) שהופכת כל סיסמה למחרוזת קבועת-אורך שאי אפשר "להפוך אחורה" בחזרה לסיסמה המקורית
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def get_user(self, username: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT username, password_hash, rating FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None:
            return None
        return {
            "username": row[0],
            "password_hash": row[1],
            "rating": row[2],
        }

    #מוסיפה משתמש חדש לטבלה
    def register(self, username: str, password: str, rating: int = DEFAULT_RATING) -> dict:
        password_hash = self.hash_password(password)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, rating) VALUES (?, ?, ?)",
                (username, password_hash, rating),
            )
            conn.commit()
        return {"username": username, "rating": rating, "created": True}

    def authenticate_or_register(self, username: str, password: str) -> dict:
        """
        Existing user: verify password.
        New user: auto-register with rating 1200.
        """
        username = username.strip()
        if not username:
            return {"ok": False, "detail": "username required"}
        if not password:
            return {"ok": False, "detail": "password required"}

        user = self.get_user(username)
        if user is None:
            created = self.register(username, password, DEFAULT_RATING)
            return {
                "ok": True,
                "username": created["username"],
                "rating": created["rating"],
                "created": True,
            }

        if user["password_hash"] != self.hash_password(password):
            return {"ok": False, "detail": "Incorrect password."}

        return {
            "ok": True,
            "username": user["username"],
            "rating": user["rating"],
            "created": False,
        }

    def set_rating(self, username: str, rating: int):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET rating = ? WHERE username = ?",
                (int(rating), username),
            )
            conn.commit()

    #פונקציית עזר נוחה שמחזירה רק את הדירוג
    def get_rating(self, username: str) -> int | None:
        user = self.get_user(username)
        return None if user is None else int(user["rating"])
