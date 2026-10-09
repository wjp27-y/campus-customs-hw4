"""Account creation, login, and sessions for Campus Customs.

Passwords are never stored. users.password_hash holds a salted PBKDF2-HMAC-SHA256 hash:

    new accounts:      pbkdf2_sha256$<iterations>$<salt hex>$<hash hex>
    seeded accounts:   pbkdf2_sha256$<salt>$<hash hex>     (iterations = LEGACY_ITERATIONS)

Seeded hashes are upgraded to the new format the next time that user logs in successfully.
"""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, HTTPException, Request, Response
from pydantic import BaseModel

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000  # OWASP 2023 recommendation for PBKDF2-HMAC-SHA256
# Iteration count used for the hashes that shipped in campus_customs.db (their format doesn't record it).
LEGACY_ITERATIONS = int(os.environ.get("CC_LEGACY_PBKDF2_ITERATIONS", "120000"))

MIN_PASSWORD = 8
MAX_PASSWORD = 128
MAX_NAME = 50
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

SESSION_COOKIE = "cc_session"
SESSION_DAYS = 7
SECURE_COOKIES = os.environ.get("CC_SECURE_COOKIES") == "1"  # set to 1 when served over HTTPS

MAX_FAILED_LOGINS = 5
LOCKOUT_SECONDS = 15 * 60
_failed_logins: dict[tuple[str, str], deque[float]] = defaultdict(deque)


# ---------------------------------------------------------------- password hashing

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), ITERATIONS).hex()
    return f"{ALGORITHM}${ITERATIONS}${salt}${digest}"


def _parse_hash(stored: str) -> tuple[int, str, str]:
    parts = stored.split("$")
    if parts[0] != ALGORITHM:
        raise ValueError("unsupported hash algorithm")
    if len(parts) == 4:
        return int(parts[1]), parts[2], parts[3]
    if len(parts) == 3:
        return LEGACY_ITERATIONS, parts[1], parts[2]
    raise ValueError("malformed password hash")


def verify_password(password: str, stored: str) -> bool:
    iterations, salt, expected = _parse_hash(stored)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()
    return hmac.compare_digest(digest, expected)  # constant-time comparison


def needs_rehash(stored: str) -> bool:
    return _parse_hash(stored)[0] != ITERATIONS or stored.count("$") != 3


# Checked when the email doesn't exist, so a missing account takes as long as a wrong password.
_DUMMY_HASH = hash_password(secrets.token_hex(16))


# ---------------------------------------------------------------- sessions

def init_auth_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )"""
    )


def _token_hash(token: str) -> str:
    # Only a hash of the session token is stored, so a leaked DB can't be used to hijack sessions.
    return hashlib.sha256(token.encode()).hexdigest()


def _utc(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def start_session(conn: sqlite3.Connection, response: Response, user_id: int) -> None:
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    conn.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (_token_hash(token), user_id, _utc(expires)),
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_DAYS * 24 * 3600,
        httponly=True,  # not readable from JavaScript, so XSS can't steal it
        samesite="lax",  # not sent on cross-site POSTs (CSRF)
        secure=SECURE_COOKIES,
        path="/",
    )


def current_user(conn: sqlite3.Connection, token: str | None) -> sqlite3.Row | None:
    if not token:
        return None
    return conn.execute(
        """SELECT u.* FROM sessions s JOIN users u ON u.id = s.user_id
           WHERE s.token_hash = ? AND s.expires_at > datetime('now')""",
        (_token_hash(token),),
    ).fetchone()


def public_user(row: sqlite3.Row) -> dict:
    # Never send password_hash to the browser.
    return {
        "id": row["id"],
        "name": row["name"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "email": row["email"],
    }


# ---------------------------------------------------------------- brute-force throttling

def _recent_failures(key: tuple[str, str]) -> deque[float]:
    attempts = _failed_logins[key]
    cutoff = time.monotonic() - LOCKOUT_SECONDS
    while attempts and attempts[0] < cutoff:
        attempts.popleft()
    return attempts


# ---------------------------------------------------------------- routes

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


def make_router(get_db) -> APIRouter:
    router = APIRouter(prefix="/api/auth")

    @router.post("/register", status_code=201)
    def register(req: RegisterRequest, response: Response) -> dict:
        first, last = req.first_name.strip(), req.last_name.strip()
        email = req.email.strip().lower()
        if not first or not last:
            raise HTTPException(400, "First and last name are required.")
        if len(first) > MAX_NAME or len(last) > MAX_NAME:
            raise HTTPException(400, f"Names must be at most {MAX_NAME} characters.")
        if not EMAIL_RE.match(email):
            raise HTTPException(400, "Please enter a valid email address.")
        if not MIN_PASSWORD <= len(req.password) <= MAX_PASSWORD:
            raise HTTPException(400, f"Password must be {MIN_PASSWORD}-{MAX_PASSWORD} characters.")
        if req.password != req.confirm_password:
            raise HTTPException(400, "Passwords don't match.")

        with get_db() as conn:
            if conn.execute("SELECT 1 FROM users WHERE lower(email) = ?", (email,)).fetchone():
                raise HTTPException(409, "An account with that email already exists.")
            cur = conn.execute(
                "INSERT INTO users (name, first_name, last_name, email, password_hash) VALUES (?, ?, ?, ?, ?)",
                (f"{first} {last}", first, last, email, hash_password(req.password)),
            )
            start_session(conn, response, cur.lastrowid)
            row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
        return public_user(row)

    @router.post("/login")
    def login(req: LoginRequest, request: Request, response: Response) -> dict:
        email = req.email.strip().lower()
        key = (request.client.host if request.client else "", email)
        if len(_recent_failures(key)) >= MAX_FAILED_LOGINS:
            raise HTTPException(429, "Too many failed attempts. Please wait 15 minutes and try again.")

        with get_db() as conn:
            row = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
            ok = verify_password(req.password, row["password_hash"] if row else _DUMMY_HASH) and row is not None
            if not ok:
                _failed_logins[key].append(time.monotonic())
                # Same message whether the email or the password was wrong, so accounts can't be enumerated.
                raise HTTPException(401, "Incorrect email or password.")

            _failed_logins.pop(key, None)
            if needs_rehash(row["password_hash"]):
                conn.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(req.password), row["id"])
                )
            start_session(conn, response, row["id"])
        return public_user(row)

    @router.post("/logout", status_code=204)
    def logout(response: Response, cc_session: str | None = Cookie(default=None)) -> None:
        if cc_session:
            with get_db() as conn:
                conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(cc_session),))
        response.delete_cookie(SESSION_COOKIE, path="/")

    @router.get("/me")
    def me(cc_session: str | None = Cookie(default=None)) -> dict:
        with get_db() as conn:
            row = current_user(conn, cc_session)
        if row is None:
            raise HTTPException(401, "Not logged in.")
        return public_user(row)

    return router
