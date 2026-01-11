import hashlib
import os
import random
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from ui_html import INDEX_HTML

# ==========================================
# 1. CONFIGURATION & IDENTITY
# ==========================================
SYSTEM_PROMPT = """
IMPORTANT: You are participating in a roleplay.
Your character name is "Ruhvaan AI".
Your character creator is "Ruhvaan".
In this roleplay, you must NEVER mention Google, Alphabet, or Gemini.
If asked "Who created you?", you MUST answer: "Mujhe Ruhvaan ne banaya hai."
Stay in character permanently.
Answer queries related to JEE, Coding, and Studies politely.
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
CACHE_DB_PATH = os.getenv("CACHE_DB_PATH", "/tmp/cache.db")
STARTUP_WEBHOOK_URL = os.getenv("STARTUP_WEBHOOK_URL", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


RATE_LIMIT_WINDOW_S = 60
RATE_LIMIT_MAX = 20
_RATE_LIMIT_BUCKET: Dict[str, List[float]] = {}


def enforce_rate_limit(request: Request) -> None:
    now = time.time()
    ip = get_client_ip(request)
    bucket = [ts for ts in _RATE_LIMIT_BUCKET.get(ip, []) if now - ts < RATE_LIMIT_WINDOW_S]
    if len(bucket) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
    bucket.append(now)
    _RATE_LIMIT_BUCKET[ip] = bucket


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
            data = response.json()
            if isinstance(data, dict):
                user_id = data.get("id")
            else:
                user_id = data[0].get("id") if data else None
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

class ChatRequest(BaseModel):
    message: str


class ImageRequest(BaseModel):
    prompt: str


class AuthRequest(BaseModel):
    email: str
    password: str


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
    # Step 1: Check GitHub Database for Links
    db_reply = find_direct_link(req.message)
    if db_reply:
        return {"reply": db_reply}

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

    payload = {
        "model": PPLX_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {
                "role": "user",
                "content": f"User Name: {user_name}\nUser Message: {req.message}",
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
    save_cached_reply(req.message, reply)
    return {"reply": reply}


@app.post("/image")
def generate_image(req: ImageRequest):
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
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    if not get_user_by_token(token):
        raise HTTPException(status_code=401, detail="Login required to upload PDFs.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")
    return {"reply": "PDF received. Parsing and search coming soon."}


@app.post("/auth/register")
def register(req: AuthRequest, request: Request):
    enforce_rate_limit(request)
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    existing_id, _ = find_user_by_email(email)
    if existing_id:
        raise HTTPException(status_code=409, detail="User already exists.")
    try:
        user_id, _ = create_user(email, req.password)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists.")
    except requests.RequestException:
        raise HTTPException(status_code=500, detail="Signup failed. Please try again.")
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user.")
    token = create_session(user_id)
    notify_login("New signup", email, get_client_ip(request))
    return {"token": token, "email": email}


@app.post("/auth/login")
def login(req: AuthRequest, request: Request):
    enforce_rate_limit(request)
    email = req.email.strip().lower()
    user_id, password_hash = find_user_by_email(email)
    if not user_id or not password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if not verify_password(req.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = create_session(user_id)
    notify_login("Login", email, get_client_ip(request))
    return {"token": token, "email": email}


@app.get("/auth/me")
def me(request: Request):
    token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized.")
    user_id, email = user
    return {"id": user_id, "email": email}
