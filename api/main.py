import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.agent import run_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_input: str
    session_id: str


@app.get("/")
def root():
    return {"message": "AI Travel Planner API is running"}


# Main endpoint
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        response = run_agent(req.user_input, req.session_id)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}