from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import google.generativeai as genai
import os

# --- SETUP ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Yahan apni API Key daalni hai (Inverted commas ke andar)
GEMINI_API_KEY = "AIzaSyCbsW2SEGvjUU-FBOTeOKB_rn8fBdcjtC4" 
genai.configure(api_key=GEMINI_API_KEY)

# Model select kiya
model = genai.GenerativeModel('gemini-pro')

class ChatRequest(BaseModel):
    message: str

# --- SYSTEM PROMPT (Ruhvaan ki personality) ---
SYSTEM_INSTRUCTION = """
Tum Ruhvaan AI ho, ek helpful aur friendly assistant.
Tum Hinglish (Hindi + English) me baat karte ho.
Tumhara goal hai student ki help karna, chahe wo coding ho, physics ho ya life advice.
Agar koi puche tum kaise bane, to bolo 'Mujhe mere Creator ne Python se banaya hai'.
"""

chat_history = [] # Choti memory (jab tak server restart na ho)

@app.get("/")
def home():
    return {"status": "Ruhvaan is Alive & Ready"}

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_text = req.message
    
    # History build karte hain taaki purani baat yaad rahe
    history_text = SYSTEM_INSTRUCTION + "\n\n"
    for msg in chat_history[-5:]: # Last 5 messages yaad rakhega
        history_text += f"{msg['role']}: {msg['text']}\n"
    
    history_text += f"User: {user_text}\nRuhvaan:"

    try:
        # Gemini se jawaab maango
        response = model.generate_content(history_text)
        reply = response.text
        
        # History save karo
        chat_history.append({"role": "User", "text": user_text})
        chat_history.append({"role": "Ruhvaan", "text": reply})
        
        return {"reply": reply}
    except Exception as e:
        return {"reply": "Sorry, abhi server busy hai ya API Key me issue hai."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)

