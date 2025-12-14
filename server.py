import os
import traceback
import random
import time
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from google.api_core import exceptions
from apitally.fastapi import ApitallyMiddleware

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
API_KEYS = [
    "AIzaSyBudxqpsvYsA1fmU-aQVc7xk4-gZNGuDEA",
    "AIzaSyA2T4nIzbLnNaJjio5tRpczgUmV06X9-EI",
    "AIzaSyBIujA85up7attURY1h1ceRuZmCm2VYZbk",
    "AIzaSyDXx1hZGmzc9aA2DZhHTUjZmTKGD7yQIhU",
    "AIzaSyAD_q1zrBv3Einkv-jlXMzj361XwCgbeOQ",
]
current_key_index = 0

app = FastAPI()

# --- APITALLY SETUP ---
app.add_middleware(
    ApitallyMiddleware,
    client_id="ac99f15e-6633-41ed-92bc-35f401b38179", # <--- YAHAN ID DALO
    env="prod",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def get_next_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return API_KEYS[current_key_index]

def extract_user_name(message: str) -> str | None:
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

    # Step 2: Ask AI (with Fallback Models)
    global current_key_index
    
    models_priority = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-pro"]

    for attempt in range(len(API_KEYS)):
        active_key = API_KEYS[current_key_index]
        genai.configure(api_key=active_key)
        
        # Smart Model Selection
        model = None
        for m_name in models_priority:
            try:
                model = genai.GenerativeModel(m_name)
                break 
            except: continue
        
        if not model:
            # Last Resort
            model = genai.GenerativeModel("gemini-1.5-flash")

        try:
            user_name = extract_user_name(req.message) or "Bhai"
            
            full_prompt = f"""
            {SYSTEM_PROMPT}
            User Name: {user_name}
            User Message: {req.message}
            Assistant:
            """

            resp = model.generate_content(full_prompt)
            reply = (getattr(resp, "text", "") or "").strip()

            # Branding
            reply = reply.replace("Google", "Ruhvaan").replace("Gemini", "Ruhvaan AI")
            
            return {"reply": reply}

        except exceptions.ResourceExhausted:
            get_next_key()
            time.sleep(0.5)
            continue
            
        except Exception as e:
            get_next_key()
            time.sleep(0.5)
            if attempt == len(API_KEYS) - 1:
                return {"reply": "Sorry bhai, server thoda busy hai. Thodi der baad try karna."}
