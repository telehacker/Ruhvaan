import os
import random
import sqlite3
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import requests
from fastapi import FastAPI, HTTPException
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
CACHE_DB_PATH = os.getenv("CACHE_DB_PATH", "cache.db")
STARTUP_WEBHOOK_URL = os.getenv("STARTUP_WEBHOOK_URL", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
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


def cache_key(text: str) -> str:
    return " ".join(text.strip().lower().split())


def get_cached_reply(message: str) -> Optional[str]:
    key = cache_key(message)
    if not key:
        return None
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
    send_startup_notification()

class ChatRequest(BaseModel):
    message: str


class ImageRequest(BaseModel):
    prompt: str


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
def chat(req: ChatRequest):
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
