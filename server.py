import hashlib
from io import BytesIO
import os
import random
import secrets
import sqlite3
import smtplib
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel
from PyPDF2 import PdfReader

from ui_html import INDEX_HTML

# ==========================================
# 1. CONFIGURATION & IDENTITY
# ==========================================
SYSTEM_PROMPT = """
IMPORTANT: You are participating in a roleplay.
Your character name is "Ruhvaan AI".
Your character creator is "Vivek".
In this roleplay, you must NEVER mention Google, Alphabet, or Gemini.
If asked "Who created you?", you MUST answer: "Mujhe Vivek ne banaya hai."
Stay in character permanently.
Answer queries related to JEE, NEET, College, Coding, and Studies politely.
Keep responses short and simple (2-4 lines max). Avoid long paragraphs.
"""

# ==========================================
# 2. DYNAMIC DATABASE (FROM GITHUB)
# ==========================================
# Ye URL tumhare 'links.json' file ka hona chahiye (Raw version)
GITHUB_DB_URL = "https://raw.githubusercontent.com/telehacker/Ruhvaan/main/links.json"

def get_latest_links():
    """GitHub se latest links fetch karta hai"""
    try:
        # 2 Second ka timeout taaki server slow na ho
        response = requests.get(GITHUB_DB_URL, timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass # Agar GitHub down hai, to purana data use karo ya ignore karo
    return {}

# Fallback Database (Agar GitHub na chale)
FALLBACK_DB = {
    "telegram": "https://t.me/Ruhvaan",
    "notes": "Please check GitHub links.json",
}

def find_direct_link(message: str):
    """User ke message me keyword dhund kar link dega"""
    msg = message.lower().strip()
    
    # 1. Pehle GitHub se Latest Data Try karo
    live_db = get_latest_links()
    
    # 2. Agar GitHub khali hai, to Fallback use karo
    if not live_db:
        live_db = FALLBACK_DB
        
    for key, link in live_db.items():
        if key in msg:
            return (
                f"✅ **Resource Found!**\n\n"
                f"Here is the link for **{key.title()}**:\n"
                f"🔗 [Click to Open]({link})\n\n"
                f"Padhai shuru karo bhai! 🚀"
            )
    return None

# ==========================================
# 3. API KEYS & APP SETUP
# ==========================================
PPLX_API_URL = "https://api.perplexity.ai/chat/completions"
PPLX_API_KEY = os.getenv("PPLX_API_KEY", "").strip()
PPLX_MODEL = os.getenv("PPLX_MODEL", "sonar")
if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
    DEFAULT_CACHE_DB_PATH = Path("/tmp/cache.db")
else:
    DEFAULT_CACHE_DB_PATH = Path(__file__).resolve().parent / "data" / "cache.db"
CACHE_DB_PATH = os.getenv("CACHE_DB_PATH", str(DEFAULT_CACHE_DB_PATH))
STARTUP_WEBHOOK_URL = os.getenv("STARTUP_WEBHOOK_URL", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASS = os.getenv("SMTP_PASS", "").strip()
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER).strip()
OTP_DEBUG_RETURN_CODE = os.getenv("OTP_DEBUG_RETURN_CODE", "false").strip().lower() == "true"
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").strip().lower() == "true"
# Optional API keys for multiple AI providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY", "").strip()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
XAI_API_KEY = os.getenv("XAI_API_KEY", "").strip()
AI21_API_KEY = os.getenv("AI21_API_KEY", "").strip()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "").strip()
REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "").strip()
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "").strip()
NOMIC_API_KEY = os.getenv("NOMIC_API_KEY", "").strip()
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY", "").strip()
JINA_API_KEY = os.getenv("JINA_API_KEY", "").strip()
COGNEURA_API_KEY = os.getenv("COGNEURA_API_KEY", "").strip()
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app = FastAPI()

Path(CACHE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=bool(ALLOWED_ORIGINS),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def apply_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    return response

def init_cache_db() -> None:
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_cache (
                    question TEXT PRIMARY KEY,
                    answer TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    last_login REAL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pdf_docs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_codes (
                    email TEXT PRIMARY KEY,
                    code_hash TEXT NOT NULL,
                    expires_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    email TEXT,
                    ip TEXT,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS shared_pdfs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    content_text TEXT NOT NULL,
                    content_blob BLOB NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
    except sqlite3.Error:
        pass


def cache_key(text: str) -> str:
    return " ".join(text.strip().lower().split())


def hash_password(password: str, salt: Optional[str] = None) -> str:
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, expected = password_hash.split("$", 1)
    except ValueError:
        return False
    candidate = hash_password(password, salt)
    return secrets.compare_digest(candidate, f"{salt}${expected}")


def is_valid_gmail(email: str) -> bool:
    return email.endswith("@gmail.com")


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def store_auth_code(email: str, code: str, ttl_seconds: int = 600) -> None:
    expires_at = time.time() + ttl_seconds
    code_hash = hash_code(code)
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO auth_codes (email, code_hash, expires_at)
                VALUES (?, ?, ?)
                """,
                (email, code_hash, expires_at),
            )
    except sqlite3.Error:
        pass


def verify_auth_code(email: str, code: str) -> bool:
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            row = conn.execute(
                "SELECT code_hash, expires_at FROM auth_codes WHERE email = ?",
                (email,),
            ).fetchone()
    except sqlite3.Error:
        return False
    if not row:
        return False
    code_hash, expires_at = row
    if time.time() > float(expires_at):
        return False
    return secrets.compare_digest(code_hash, hash_code(code))


def supabase_headers() -> Dict[str, str]:
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


RATE_LIMIT_WINDOW_S = int(os.getenv("RATE_LIMIT_WINDOW_S", "60"))
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "20"))
RATE_LIMIT_MAX_GUEST = int(os.getenv("RATE_LIMIT_MAX_GUEST", "10"))
_RATE_LIMIT_BUCKET: Dict[str, List[float]] = {}
_RATE_LIMIT_BUCKET_TOKEN: Dict[str, List[float]] = {}


def get_bearer_token(request: Request) -> str:
    return request.headers.get("authorization", "").removeprefix("Bearer ").strip()


def enforce_rate_limit(request: Request) -> None:
    now = time.time()
    ip = get_client_ip(request)
    token = get_bearer_token(request)
    bucket = [ts for ts in _RATE_LIMIT_BUCKET.get(ip, []) if now - ts < RATE_LIMIT_WINDOW_S]
    ip_limit = RATE_LIMIT_MAX if token else RATE_LIMIT_MAX_GUEST
    if len(bucket) >= ip_limit:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
    bucket.append(now)
    _RATE_LIMIT_BUCKET[ip] = bucket
    if token:
        token_bucket = [
            ts for ts in _RATE_LIMIT_BUCKET_TOKEN.get(token, []) if now - ts < RATE_LIMIT_WINDOW_S
        ]
        if len(token_bucket) >= RATE_LIMIT_MAX:
            raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
        token_bucket.append(now)
        _RATE_LIMIT_BUCKET_TOKEN[token] = token_bucket


def require_authenticated_user(request: Request) -> Tuple[int, str]:
    token = get_bearer_token(request)
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    return user


def create_user(email: str, password: str) -> Tuple[Optional[int], str]:
    password_hash = hash_password(password)
    created_at = time.time()
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/users",
                headers=supabase_headers(),
                json={"email": email, "password_hash": password_hash, "created_at": created_at},
                timeout=5,
            )
            response.raise_for_status()
            try:
                data = response.json()
            except ValueError:
                data = []
            if isinstance(data, dict):
                user_id = data.get("id")
            else:
                user_id = data[0].get("id") if data else None
            if user_id:
                return user_id, password_hash
        except requests.RequestException:
            pass
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email, password_hash, created_at),
        )
        return cursor.lastrowid, password_hash


def find_user_by_email(email: str) -> Tuple[Optional[int], Optional[str]]:
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/users",
                headers=supabase_headers(),
                params={"email": f"eq.{email}", "select": "id,password_hash"},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                return None, None
            return data[0].get("id"), data[0].get("password_hash")
        except requests.RequestException:
            pass
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (email,),
        ).fetchone()
    return (row[0], row[1]) if row else (None, None)


def update_user_password(email: str, password: str) -> None:
    password_hash = hash_password(password)
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/users",
                headers=supabase_headers(),
                params={"email": f"eq.{email}"},
                json={"password_hash": password_hash},
                timeout=5,
            ).raise_for_status()
            return
        except requests.RequestException:
            pass
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (password_hash, email),
        )


def create_session(user_id: int) -> str:
    token = secrets.token_hex(24)
    created_at = time.time()
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            requests.post(
                f"{SUPABASE_URL}/rest/v1/sessions",
                headers=supabase_headers(),
                json={"token": token, "user_id": user_id, "created_at": created_at},
                timeout=5,
            ).raise_for_status()
            return token
        except requests.RequestException:
            pass
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, user_id, created_at),
        )
    return token


def get_user_by_token(token: str) -> Optional[Tuple[int, str]]:
    if not token:
        return None
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/sessions",
                headers=supabase_headers(),
                params={"token": f"eq.{token}", "select": "user_id"},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            if not data:
                return None
            user_id = data[0].get("user_id")
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/users",
                headers=supabase_headers(),
                params={"id": f"eq.{user_id}", "select": "id,email"},
                timeout=5,
            )
            response.raise_for_status()
            user = response.json()
            if not user:
                return None
            return user[0].get("id"), user[0].get("email")
        except requests.RequestException:
            pass
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT users.id, users.email
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (token,),
        ).fetchone()
    return (row[0], row[1]) if row else None


def update_last_login(email: str) -> None:
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/users",
                headers=supabase_headers(),
                params={"email": f"eq.{email}"},
                json={"last_login": time.time()},
                timeout=5,
            ).raise_for_status()
            return
        except requests.RequestException:
            pass
    with sqlite3.connect(CACHE_DB_PATH) as conn:
        conn.execute(
            "UPDATE users SET last_login = ? WHERE email = ?",
            (time.time(), email),
        )


def save_pdf_doc(user_id: int, filename: str, content: str) -> None:
    created_at = time.time()
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            requests.post(
                f"{SUPABASE_URL}/rest/v1/pdf_docs",
                headers=supabase_headers(),
                json={
                    "user_id": user_id,
                    "filename": filename,
                    "content": content,
                    "created_at": created_at,
                },
                timeout=10,
            ).raise_for_status()
            return
        except requests.RequestException:
            pass
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO pdf_docs (user_id, filename, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, filename, content, created_at),
            )
    except sqlite3.Error:
        return


def get_pdf_docs(user_id: int) -> List[Dict[str, str]]:
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/pdf_docs",
                headers=supabase_headers(),
                params={"user_id": f"eq.{user_id}", "select": "filename,content"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return data or []
        except requests.RequestException:
            pass
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            rows = conn.execute(
                "SELECT filename, content FROM pdf_docs WHERE user_id = ?",
                (user_id,),
            ).fetchall()
        return [{"filename": row[0], "content": row[1]} for row in rows]
    except sqlite3.Error:
        return []


def save_shared_pdf(filename: str, content_text: str, content_blob: bytes) -> None:
    created_at = time.time()
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO shared_pdfs (filename, content_text, content_blob, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (filename, content_text, sqlite3.Binary(content_blob), created_at),
            )
    except sqlite3.Error:
        return


def get_shared_pdfs(limit: int = 20) -> List[Dict[str, str]]:
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            rows = conn.execute(
                """
                SELECT id, filename, created_at
                FROM shared_pdfs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    except sqlite3.Error:
        return []
    return [
        {"id": row[0], "filename": row[1], "created_at": row[2]}
        for row in rows
    ]


def get_shared_pdf_content(pdf_id: int) -> Optional[Tuple[str, bytes]]:
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            row = conn.execute(
                "SELECT filename, content_blob FROM shared_pdfs WHERE id = ?",
                (pdf_id,),
            ).fetchone()
    except sqlite3.Error:
        return None
    return (row[0], row[1]) if row else None


def get_shared_pdf_context() -> str:
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            rows = conn.execute(
                """
                SELECT content_text
                FROM shared_pdfs
                ORDER BY created_at DESC
                LIMIT 3
                """
            ).fetchall()
    except sqlite3.Error:
        return ""
    combined = "\n\n".join(row[0] for row in rows if row and row[0])
    return combined[:4000]


def get_cached_reply(message: str) -> Optional[str]:
    key = cache_key(message)
    if not key:
        return None
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/qa_cache",
                headers=supabase_headers(),
                params={"question": f"eq.{key}", "select": "answer"},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0].get("answer")
        except requests.RequestException:
            pass
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            row = conn.execute(
                "SELECT answer FROM qa_cache WHERE question = ?",
                (key,),
            ).fetchone()
    except sqlite3.Error:
        return None
    return row[0] if row else None


def save_cached_reply(question: str, answer: str) -> None:
    key = cache_key(question)
    if not key or not answer:
        return
    if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
        try:
            requests.post(
                f"{SUPABASE_URL}/rest/v1/qa_cache",
                headers=supabase_headers(),
                json={
                    "question": key,
                    "answer": answer,
                    "created_at": time.time(),
                },
                timeout=5,
            )
            return
        except requests.RequestException:
            pass
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO qa_cache (question, answer, created_at)
                VALUES (?, ?, ?)
                """,
                (key, answer, time.time()),
            )
    except sqlite3.Error:
        return


def send_startup_notification() -> None:
    message = "Ruhvaan bot started successfully."
    if STARTUP_WEBHOOK_URL:
        try:
            requests.post(
                STARTUP_WEBHOOK_URL,
                json={"text": message},
                timeout=5,
            )
        except requests.RequestException:
            pass
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
                timeout=5,
            )
        except requests.RequestException:
            pass


@app.on_event("startup")
def on_startup() -> None:
    init_cache_db()
    try:
        send_startup_notification()
    except requests.RequestException:
        pass


def notify_login(event: str, email: str, ip: Optional[str] = None) -> None:
    message = f"{event}: {email}"
    if ip:
        message = f"{message} ({ip})"
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
                timeout=5,
            )
        except requests.RequestException:
            pass
    log_activity(event, email, ip)


def notify_ai_usage(actor: str, message: str, ip: Optional[str] = None) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    summary = message.strip().replace("\n", " ")
    summary = summary[:500] + ("…" if len(summary) > 500 else "")
    text = f"AI used by {actor}"
    if ip:
        text = f"{text} ({ip})"
    text = f"{text}\nMessage: {summary}"
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text},
            timeout=5,
        )
    except requests.RequestException:
        pass
    log_activity("AI usage", actor, ip)


def log_activity(event: str, email: Optional[str], ip: Optional[str]) -> None:
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO activity_logs (event, email, ip, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (event, email, ip, time.time()),
            )
    except sqlite3.Error:
        pass


def send_email_code(email: str, code: str) -> None:
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS or not SMTP_FROM:
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": f"Verification code for {email}: {code}",
                    },
                    timeout=5,
                )
                return
            except requests.RequestException:
                pass
        missing_vars = []
        if not SMTP_HOST:
            missing_vars.append("SMTP_HOST")
        if not SMTP_USER:
            missing_vars.append("SMTP_USER")
        if not SMTP_PASS:
            missing_vars.append("SMTP_PASS")
        if not SMTP_FROM:
            missing_vars.append("SMTP_FROM")
        missing_hint = ", ".join(missing_vars) if missing_vars else "SMTP configuration"
        raise HTTPException(
            status_code=500,
            detail=(
                "Email service not configured. Missing: "
                f"{missing_hint}. Set SMTP_* env vars or configure Telegram fallback."
            ),
        )
    message = (
        "Subject: Ruhvaan AI Verification Code\r\n"
        f"From: {SMTP_FROM}\r\n"
        f"To: {email}\r\n\r\n"
        "Your verification code is:\r\n"
        f"{code}\r\n\r\n"
        "This code expires in 10 minutes."
    )
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_FROM, [email], message)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_FROM, [email], message)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to send verification code. Verify SMTP host, port, and "
                "credentials. For Gmail, use an App Password (2FA) with port "
                "587 (STARTTLS) or 465 (SSL)."
            ),
        )

class ChatRequest(BaseModel):
    message: str


class ImageRequest(BaseModel):
    prompt: str


class AuthRequest(BaseModel):
    email: str
    password: str


class AuthCodeRequest(BaseModel):
    email: str


class AuthRegisterRequest(BaseModel):
    email: str
    password: str
    code: str


class AuthResetRequest(BaseModel):
    email: str
    password: str
    code: str


@app.get("/")
def root():
    index_path = Path(__file__).resolve().parent / "index.html"
    if index_path.is_file():
        return FileResponse(index_path)
    return HTMLResponse(INDEX_HTML)


@app.get("/favicon.ico")
def favicon():
    return PlainTextResponse("", status_code=204)

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def extract_user_name(message: str) -> Optional[str]:
    text = message.strip().lower()
    patterns = ["mera naam", "my name is", "i am ", "main "]
    for p in patterns:
        if p in text:
            try:
                idx = text.find(p) + len(p)
                return message[idx:].split()[0].strip(".,!")
            except: pass
    return None

# ==========================================
# 5. MAIN CHAT ROUTE
# ==========================================
@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    enforce_rate_limit(request)
    token = get_bearer_token(request)
    user = get_user_by_token(token)
    if REQUIRE_AUTH and not user:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    if user:
        update_last_login(user[1])
        log_activity("Chat message", user[1], get_client_ip(request))
    # Step 1: Check GitHub Database for Links
    db_reply = find_direct_link(req.message)
    if db_reply:
        return {"reply": db_reply}

    shared_items = get_shared_pdfs(limit=5)
    if shared_items and any(key in req.message.lower() for key in ["pdf", "question", "questions", "chapter"]):
        links = "\n".join(
            f"• {item['filename']} (ID: {item['id']})"
            for item in shared_items
        )
        return {
            "reply": (
                "Yeh shared PDFs available hain:\n"
                f"{links}\n"
                "Shared PDFs panel se download karo, phir name batao to main explain kar dunga."
            )
        }

    cached_reply = get_cached_reply(req.message)
    if cached_reply:
        return {"reply": cached_reply}

    # Step 2: Ask AI (Perplexity)
    if not PPLX_API_KEY:
        return {
            "reply": (
                "Server configuration missing PPLX_API_KEY. "
                "Please add it to the backend environment."
            )
        }
    user_name = extract_user_name(req.message) or "Bhai"
    actor = user[1] if user else f"guest:{get_client_ip(request)}"
    notify_ai_usage(actor, req.message, get_client_ip(request))

    pdf_context = ""
    if user:
        docs = get_pdf_docs(user[0])
        if docs:
            combined = "\n\n".join(doc["content"] for doc in docs)
            pdf_context = combined[:4000]
    shared_context = get_shared_pdf_context()

    payload = {
        "model": PPLX_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {
                "role": "user",
                "content": (
                    f"User Name: {user_name}\n"
                    f"User Message: {req.message}\n"
                    f"{'PDF Context:\\n' + pdf_context if pdf_context else ''}"
                    f"{'\\nShared PDF Context:\\n' + shared_context if shared_context else ''}"
                ),
            },
        ],
        "temperature": 0.7,
        "max_tokens": 512,
    }

    try:
        response = requests.post(
            PPLX_API_URL,
            headers={"Authorization": f"Bearer {PPLX_API_KEY}"},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        reply = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
    except requests.RequestException:
        time.sleep(0.5)
        return {"reply": "Sorry bhai, server thoda busy hai. Thodi der baad try karna."}

    # Branding
    reply = reply.replace("Google", "Ruhvaan").replace("Gemini", "Ruhvaan AI")
    reply_lines = [line.strip() for line in reply.splitlines() if line.strip()]
    if reply_lines:
        reply = "\n".join(reply_lines[:4])
        if len(reply) > 400:
            reply = reply[:400].rsplit(" ", 1)[0] + "..."
    save_cached_reply(req.message, reply)
    return {"reply": reply}


@app.post("/image")
def generate_image(req: ImageRequest, request: Request):
    if REQUIRE_AUTH:
        require_authenticated_user(request)
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")

    seed = random.randint(1, 999999)
    safe_prompt = quote(prompt)
    image_url = (
        "https://image.pollinations.ai/prompt/"
        f"{safe_prompt}?width=768&height=768&seed={seed}"
    )
    return {"image_url": image_url}


@app.post("/upload")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    enforce_rate_limit(request)
    token = get_bearer_token(request)
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Login required to upload PDFs.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    text_chunks = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text:
            text_chunks.append(page_text)
    full_text = "\n".join(text_chunks).strip()
    if not full_text:
        raise HTTPException(status_code=400, detail="Could not read text from this PDF.")
    save_pdf_doc(user[0], file.filename or "document.pdf", full_text)
    notify_ai_usage(user[1], f"Uploaded PDF: {file.filename or 'document.pdf'}", get_client_ip(request))
    return {
        "reply": "PDF uploaded successfully. Ask a question and I will use it for answers."
    }


@app.post("/admin/shared-pdf")
async def admin_shared_pdf(request: Request, file: UploadFile = File(...)):
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    text_chunks = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text:
            text_chunks.append(page_text)
    full_text = "\n".join(text_chunks).strip()
    if not full_text:
        raise HTTPException(status_code=400, detail="Could not read text from this PDF.")
    save_shared_pdf(file.filename or "shared.pdf", full_text, content)
    return {"message": "Shared PDF uploaded."}


@app.get("/shared-pdfs")
def list_shared_pdfs(request: Request):
    if REQUIRE_AUTH:
        require_authenticated_user(request)
    return {"items": get_shared_pdfs()}


@app.get("/shared-pdfs/{pdf_id}/download")
def download_shared_pdf(pdf_id: int, request: Request):
    if REQUIRE_AUTH:
        require_authenticated_user(request)
    result = get_shared_pdf_content(pdf_id)
    if not result:
        raise HTTPException(status_code=404, detail="PDF not found.")
    filename, content = result
    return StreamingResponse(
        BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.post("/auth/register")
def register(req: AuthRegisterRequest, request: Request):
    enforce_rate_limit(request)
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required.")
    if not is_valid_gmail(email):
        raise HTTPException(status_code=400, detail="Only @gmail.com emails are allowed.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if not req.code:
        raise HTTPException(status_code=400, detail="Verification code is required.")
    if not verify_auth_code(email, req.code.strip()):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code.")
    existing_id, _ = find_user_by_email(email)
    if existing_id:
        raise HTTPException(
            status_code=409,
            detail="User already exists. Please login or use Forgot Password.",
        )
    try:
        user_id, _ = create_user(email, req.password)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="User already exists. Please login or use Forgot Password.",
        )
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Signup failed. Please try again.")
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user.")
    token = create_session(user_id)
    update_last_login(email)
    notify_login("New signup", email, get_client_ip(request))
    return {"token": token, "email": email}


@app.post("/auth/login")
def login(req: AuthRequest, request: Request):
    enforce_rate_limit(request)
    email = req.email.strip().lower()
    if not is_valid_gmail(email):
        raise HTTPException(status_code=400, detail="Only @gmail.com emails are allowed.")
    user_id, password_hash = find_user_by_email(email)
    if not user_id or not password_hash:
        raise HTTPException(status_code=404, detail="No account found. Please sign up.")
    if not verify_password(req.password, password_hash):
        raise HTTPException(status_code=401, detail="Wrong password. Please try again.")
    token = create_session(user_id)
    update_last_login(email)
    notify_login("Login", email, get_client_ip(request))
    return {"token": token, "email": email}


@app.post("/auth/request-code")
def request_code(req: AuthCodeRequest, request: Request):
    enforce_rate_limit(request)
    email = req.email.strip().lower()
    if not is_valid_gmail(email):
        raise HTTPException(status_code=400, detail="Only @gmail.com emails are allowed.")
    code = f"{random.randint(1000, 9999)}"
    store_auth_code(email, code)
    try:
        send_email_code(email, code)
        return {"message": "Verification code sent."}
    except HTTPException as exc:
        if exc.status_code == 500 and str(exc.detail).startswith("Email service not configured"):
            response = {"message": str(exc.detail)}
            if OTP_DEBUG_RETURN_CODE:
                response["debug_code"] = code
            return response
        raise


@app.post("/auth/request-reset-code")
def request_reset_code(req: AuthCodeRequest, request: Request):
    enforce_rate_limit(request)
    email = req.email.strip().lower()
    if not is_valid_gmail(email):
        raise HTTPException(status_code=400, detail="Only @gmail.com emails are allowed.")
    user_id, _ = find_user_by_email(email)
    if not user_id:
        raise HTTPException(status_code=404, detail="No account found for this email.")
    code = f"{random.randint(1000, 9999)}"
    store_auth_code(email, code)
    try:
        send_email_code(email, code)
        return {"message": "Verification code sent."}
    except HTTPException as exc:
        if exc.status_code == 500 and str(exc.detail).startswith("Email service not configured"):
            response = {"message": str(exc.detail)}
            if OTP_DEBUG_RETURN_CODE:
                response["debug_code"] = code
            return response
        raise


@app.post("/auth/reset-password")
def reset_password(req: AuthResetRequest, request: Request):
    enforce_rate_limit(request)
    email = req.email.strip().lower()
    if not is_valid_gmail(email):
        raise HTTPException(status_code=400, detail="Only @gmail.com emails are allowed.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if not req.code:
        raise HTTPException(status_code=400, detail="Verification code is required.")
    if not verify_auth_code(email, req.code.strip()):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code.")
    user_id, _ = find_user_by_email(email)
    if not user_id:
        raise HTTPException(status_code=404, detail="No account found for this email.")
    update_user_password(email, req.password)
    notify_login("Password reset", email, get_client_ip(request))
    return {"message": "Password updated."}


@app.get("/admin/activity")
def activity(request: Request, limit: int = 50):
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            rows = conn.execute(
                """
                SELECT event, email, ip, created_at
                FROM activity_logs
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    except sqlite3.Error:
        return {"items": []}
    return {
        "items": [
            {"event": row[0], "email": row[1], "ip": row[2], "created_at": row[3]}
            for row in rows
        ]
    }


@app.get("/admin/stats")
def admin_stats(request: Request):
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    now = time.time()
    day_ago = now - 86400
    week_ago = now - 7 * 86400
    five_min_ago = now - 300
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            active_now = conn.execute(
                "SELECT COUNT(*) FROM users WHERE last_login IS NOT NULL AND last_login >= ?",
                (five_min_ago,),
            ).fetchone()[0]
            active_day = conn.execute(
                "SELECT COUNT(*) FROM users WHERE last_login IS NOT NULL AND last_login >= ?",
                (day_ago,),
            ).fetchone()[0]
            active_week = conn.execute(
                "SELECT COUNT(*) FROM users WHERE last_login IS NOT NULL AND last_login >= ?",
                (week_ago,),
            ).fetchone()[0]
    except sqlite3.Error:
        return {"total_users": 0, "active_now": 0, "active_last_24h": 0, "active_last_7d": 0}
    return {
        "total_users": total_users,
        "active_now": active_now,
        "active_last_24h": active_day,
        "active_last_7d": active_week,
    }


@app.get("/admin/users")
def admin_users(request: Request, limit: int = 20):
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    now = time.time()
    active_threshold = now - 300
    try:
        with sqlite3.connect(CACHE_DB_PATH) as conn:
            rows = conn.execute(
                """
                SELECT email, created_at, last_login
                FROM users
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    except sqlite3.Error:
        return {"items": []}
    return {
        "items": [
            {
                "email": row[0],
                "created_at": row[1],
                "last_login": row[2],
                "is_online": bool(row[2] and row[2] >= active_threshold),
            }
            for row in rows
        ]
    }


@app.get("/auth/me")
def me(request: Request):
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    user_id, email = user
    return {"id": user_id, "email": email}
