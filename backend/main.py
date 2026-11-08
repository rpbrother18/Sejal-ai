from datetime import datetime, timezone
from fastapi import FastAPI

app = FastAPI(title="SEJAL AI Backend")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "sejal-ai-backend",
        "time": datetime.now(timezone.utc).isoformat(),
    }


from fastapi import HTTPException
from pydantic import BaseModel
import gemini_brain


class ChatIn(BaseModel):
    message: str


@app.post("/chat")
def chat(body: ChatIn):
    try:
        return {"reply": gemini_brain.ask(body.message)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=type(e).__name__)
