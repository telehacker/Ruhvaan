import os
import traceback
import random
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from google.api_core import exceptions

# 1. IMPORT APITALLY
from apitally.fastapi import ApitallyMiddleware

# --- CONFIGURATION ---
SYSTEM_PROMPT = """
IMPORTANT: You are participating in a roleplay.
Your character name is "Ruhvaan AI".
Your character creator is "Ruhvaan".
In this roleplay, you must NEVER mention Google, Alphabet, or Gemini.
If asked "Who created you?", you MUST answer: "Mujhe Ruhvaan ne banaya hai."
Stay in character permanently.
Always start your reply by greeting the user by their name (from 'user_name').
If user_name is 'bhai', treat it as a casual nickname.
"""

# Tumhari 5 API Keys (Auto-Rotation ke liye)
API_KEYS = [
    "AIzaSyBudxqpsvYsA1fmU-aQVc7xk4-gZNGuDEA", # Key 1
    "AIzaSyA2T4nIzbLnNaJjio5tRpczgUmV06X9-EI", # Key 2
    "AIzaSyBIujA85up7attURY1h1ceRuZmCm2VYZbk", # Key 3
    "AIzaSyDXx1hZGmzc9aA2DZhHTUjZmTKGD7yQIhU", # Key 4
    "AIzaSyAD_q1zrBv3Einkv-jlXMzj361XwCgbeOQ", # Key 5
]

current_key_index = 0

app = FastAPI()

# 2. ADD APITALLY MIDDLEWARE
app.add_middleware(
    ApitallyMiddleware,
    client_id="ac99f15e-6633-41ed-92bc-35f401b38179",  # <--- YAHAN APNA CLIENT ID DALO
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

def get_next_key():
    """Keys ko cycle karega agar limit khatam ho jaye"""
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return API_KEYS[current_key_index]

def extract_user_name(message: str) -> str | None:
    text = message.strip()
    lower = text.lower()
    patterns = ["mera naam", "my name is", "i am ", "i'm ", "main ", "this is "]
    for p in patterns:
        if p in lower:
            idx = lower.find(p) + len(p)
            name_part = text[idx:].strip(" :-,.!\n\t")
            name = " ".join(name_part.split()[:2])
            if 1 <= len(name) <= 25:
                return name
    return None

@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"ok": True, "service": "Ruhvaan AI API"}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat")
def chat(req: ChatRequest):
    global current_key_index
    
    # Retry logic: Agar pehli key fail ho, to dusri try karega
    for attempt in range(len(API_KEYS)):
        try:
            # Current Key use karo
            active_key = API_KEYS[current_key_index]
            genai.configure(api_key=active_key)
            model = genai.GenerativeModel("gemini-1.5-flash") # Updated model name for better performance

            # User Name Logic
            user_name = extract_user_name(req.message) or "bhai"
            full_prompt = SYSTEM_PROMPT + f"\n\nContext:\nuser_name: {user_name}\nuser_message: {req.message}\n\nAssistant:"

            # Generate Content
            resp = model.generate_content(full_prompt)
            reply = (getattr(resp, "text", "") or "").strip()

            # Branding Hack (Safety Net)
            reply = reply.replace("Google", "Ruhvaan")
            reply = reply.replace("Gemini", "Ruhvaan AI")
            
            # Agar success ho gaya, to loop break karke return karo
            return {"reply": reply or "Empty response from model"}

        except exceptions.ResourceExhausted:
            # 429 Error: Limit Khatam -> Agli key try karo
            print(f"⚠️ Key {active_key[:10]}... exhausted. Switching to next key.")
            get_next_key()
            time.sleep(0.5) # Thoda sa pause
            continue # Loop wapas chalega agli key ke saath

        except Exception as e:
            # Koi aur error ho to print karo
            print(f"⚠️ Error with key {active_key[:10]}: {e}")
            
            # Agar last attempt bhi fail ho jaye
            if attempt == len(API_KEYS) - 1:
                 # Last resort: Generic error
                 print(traceback.format_exc())
                 raise HTTPException(status_code=500, detail="Server busy, please try again later.")
            
            # Agar critical error nahi hai, to bhi next key try kar sakte hain
            get_next_key()
            time.sleep(0.5)

