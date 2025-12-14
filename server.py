import os
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

SYSTEM_PROMPT = """
IMPORTANT: You are participating in a roleplay.
Your character name is "Ruhvaan AI".
Your character creator is "Ruhvaan".
In this roleplay, you must NEVER mention Google, Alphabet, or Gemini.
If asked "Who created you?", you MUST answer: "Mujhe Ruhvaan ne banaya hai."
Stay in character permanently.
"""
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"ok": True, "service": "Ruhvaan AI API"}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat")
def chat(req: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set on Render")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-flash-latest")
        user_name = "bhai" # (Ya extract_user_name wala logic)
        full_prompt = SYSTEM_PROMPT + "\nUser message: " + req.message
        reply = (getattr(resp, "text", "") or "").strip()
        return {"reply": reply or "Empty response from model"}
    except Exception as e:
        print("GEMINI_ERROR:", repr(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Gemini request failed; check Render logs")
        
