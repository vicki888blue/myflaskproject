# auth/service.py
from flask import session
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from db import connect, transaction  # <-- use your SQLAlchemy helpers

def register_user(username: str, email: str, password: str, role_id: int = 1) -> None:
    """
    Inserts a new user with a hashed password. Raises on constraint violations.
    """
    password_hash = generate_password_hash(password)
    sql = text("""
        INSERT INTO users (username, email, password_hash, role_id, created_at)
        VALUES (:username, :email, :password_hash, :role_id, CURRENT_TIMESTAMP)
    """)
    with transaction() as conn:
        conn.execute(sql, {
            "username": username,
            "email": email or None,
            "password_hash": password_hash,
            "role_id": role_id
        })

def authenticate(username_or_email: str, password: str):
    """
    Returns dict {id, username, email, role_id} if credentials valid, else None.
    """
    sql = text("""
        SELECT id, username, email, password_hash, role_id
        FROM users
        WHERE username = :u OR email = :u
        LIMIT 1
    """)
    with connect() as conn:
        row = conn.execute(sql, {"u": username_or_email}).mappings().first()
        if not row:
            return None
        if not check_password_hash(row["password_hash"], password):
            return None
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "role_id": row["role_id"],
        }

def get_current_user():
    """
    Looks up the current user by session["user_id"].
    Returns dict {id, username, email, role_id} or None.
    """
    user_id = session.get("user_id")
    if not user_id:
        return None

    sql = text("""
        SELECT id, username, email, role_id
        FROM users
        WHERE id = :id
        LIMIT 1
    """)
    with connect() as conn:
        row = conn.execute(sql, {"id": user_id}).mappings().first()
        if not row:
            return None
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "role_id": row["role_id"],
        }