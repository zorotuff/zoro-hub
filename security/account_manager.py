import uuid
from datetime import datetime

from security.database import get_connection, ensure_db
from security.auth import hash_password, verify_password


def account_exists(username):
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username.lower(),)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def create_account(username, password):
    ensure_db()
    username = username.lower()
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()
        if existing:
            return False

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        joined = datetime.now().strftime("%B %Y")
        uid = f"NX-{uuid.uuid4().hex[:8].upper()}"

        conn.execute(
            """
            INSERT INTO users (
                username, uid, password_hash, is_admin,
                joined_date, account_creation_date, last_online
            ) VALUES (?, ?, ?, 0, ?, ?, ?)
            """,
            (username, uid, hash_password(password), joined, now, now),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def login_account(username, password):
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username.lower(),),
        ).fetchone()
        if row is None:
            return False
        return verify_password(password, row["password_hash"])
    finally:
        conn.close()


def is_admin(username):
    ensure_db()
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT is_admin FROM users WHERE username = ?",
            (username.lower(),),
        ).fetchone()
        return bool(row and row["is_admin"])
    finally:
        conn.close()
