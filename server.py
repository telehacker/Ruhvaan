from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import random
import time

app = FastAPI()

# Frontend ko connect karne ki permission (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# Ruhvaan ka brain (Abhi basic hai, baad me isme PDF/Notes jodenge)
def get_ruhvaan_reply(text):
    text = text.lower()
    
    if "hello" in text or "hi" in text:
        return "Namaste! Main Ruhvaan hoon. Boliye kaise madad karoon?"
    elif "kaise ho" in text:
        return "Main ek AI hoon, hamesha active aur seekhne ke liye taiyaar!"
    elif "date" in text or "time" in text:
        return f"Abhi system time hai: {time.strftime('%H:%M:%S')}"
    elif "bye" in text:
        return "Alvida! Phir milenge."
    elif "feature" in text:
        return "Mere paas abhi Dark Mode, Clouds, aur History save karne ki shakti hai."
    else:
        # Default responses agar samajh na aaye
        responses = [
            "Hmm, dilchasp baat hai. Thora aur batayenge?",
            "Main samajh raha hoon. Aage boliye.",
            "Ye mere knowledge base me naya hai, par main seekh raha hoon.",
            f"Aapne kaha: '{text}' - maine note kar liya hai."
        ]
        return random.choice(responses)

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # Thora wait karte hain taaki 'Thinking...' animation dikhe
    time.sleep(1) 
    reply = get_ruhvaan_reply(req.message)
    return {"reply": reply}

# Server Run karne ke liye
if __name__ == "__main__":
    print("🟢 Ruhvaan AI Server Starting...")
    print("🔗 Access at: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
