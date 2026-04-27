import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

#setting up the root directory this ensures backend modules are importable
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.agent import run_agent, generate_itinerary

app = FastAPI()

#enabling CORS (middleware) so the frontend can communicate with this API without being blocked
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_input: str = None  #for general chat
    session_id: str = "default_session"
    source: str = None
    destination: str = None
    budget: str = None
    days: str = None
    food_pref: str = None
    specs: str = None
    adults: int = 1
    children: int = 0
    travel_date: str = None
    currency: str = "INR"

@app.get("/")
def root():
    return {"message": "AI Travel Planner API is running"}

#main endpoint that decides whether to run a general chat or generate a full itinerary
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        #if the request has a source and destination, we use the specialized itinerary generator
        if req.source and req.destination:
            response = generate_itinerary(
                source=req.source,
                destination=req.destination,
                budget=req.budget,
                days=req.days,
                food_pref=req.food_pref,
                specs=req.specs,
                adults=req.adults,
                children=req.children,
                travel_date=req.travel_date,
                currency=req.currency
            )
        else:
            #fallback to general agent logic if it's just a text message
            response = run_agent(req.user_input, req.session_id)
            
        return {"response": response}
    except Exception as e:
        #catching errors to prevent the server from crashing and sending the message to the UI
        return {"error": str(e)}