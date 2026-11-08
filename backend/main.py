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


import agent


@app.post("/agent")
def agent_route(body: ChatIn):
    try:
        return agent.run(body.message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=type(e).__name__)


import memory


class MemIn(BaseModel):
    category: str
    text: str


class TextIn(BaseModel):
    text: str


@app.get("/memory")
def memory_list():
    return {"enabled": memory.is_enabled(), "items": memory.list_all()}


@app.post("/memory")
def memory_add(body: MemIn):
    return memory.add(body.category, body.text)


@app.put("/memory/{mid}")
def memory_update(mid: int, body: TextIn):
    return memory.update(mid, body.text)


@app.delete("/memory/{mid}")
def memory_delete(mid: int):
    return memory.delete(mid)


@app.post("/memory/enabled/{flag}")
def memory_enabled(flag: bool):
    return {"enabled": memory.set_enabled(flag)}
