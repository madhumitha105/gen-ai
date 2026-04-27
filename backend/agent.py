import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from backend.vector_tools import search_local_knowledge, web_search
from backend.flight_data import get_flights
from backend.memory import get_session
from backend.exchange_tool import convert_currency
from backend.weather_tool import get_weather

load_dotenv()

#choosing the LLM
llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    groq_api_key=os.getenv("RAPID_API_KEY"),
    temperature=0
)

#using local DB for planning, web search for links and get_flights for flight details
tools = [search_local_knowledge, web_search, get_flights, convert_currency, get_weather]
agent_executor = create_react_agent(llm, tools)

#cleaning the LLM's output
def clean_text(text):
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"^[\*\-]\s+", "", text, flags=re.MULTILINE)
    text = text.replace("*", "")
    return text

#running the agent using prompt
def run_agent(user_input: str, session_id: str):
    session_messages = get_session(session_id)

    system_prompt = """
### ROLE
You are an expert Local-First Travel Planner. 
Your goal is to provide highly structured, real-time travel itineraries using live data and local historical knowledge.

### OPERATIONAL PROTOCOL
1. **WEATHER CHECK**: Call `get_weather` first to determine if activities are appropriate for the current climate.
2. **CURRENCY CALCULATION**: If source and destination countries differ, use `convert_currency` to translate the user's budget.
3. **FLIGHT SEARCH**: call `get_flights` using the provided date, adults, and children.
4. **LOCAL KNOWLEDGE**: Use `search_local_knowledge` for descriptions, history, and cultural relevance of places.

### OUTPUT STRUCTURE (STRICT)

#### 1. Weather & Currency Overview
- **Forecast**: [Result from get_weather]
- **Budget**: [Source Amount] (~ [Converted Amount])

#### 2. Flight Options
- [Airline] | [Price] | [Duration]
- [Airline] | [Price] | [Duration]

#### 3. Daily Itinerary
**Day [X]**
- **Visit**: [Clean Place Name] - [One-liner description] [Clickable Markdown Link]
- **Food**: [Specific dish based on user preference]
- **Stay**: [Recommended area or type of stay]

####4. Budget
- must generate the budget in source location's currency and also mention the estimation in destination's currency. 
- example: source: Edinburgh, destination: Tokyo, budget: 3000 
- consider the number in budget as the source location's currency and plan accordingly
- OUTPUR BOTH CURRENCY ESTIMATED VALUES 

### CONSTRAINTS
- **FORMAT**: Use bullet points only. No paragraphs.
- **LINKS**: All place names must be clickable Markdown links: [Place Name](https://www.google.com/search?q=Place+Name)
- **CURRENCY**: Only show one currency if Source and Destination use the same currency. Otherwise, mandatory dual-currency display.
- **FOOD**: Strictly respect dietary preferences (e.g., Veg/Jain/Vegan).
"""

    session_messages.append(SystemMessage(content=system_prompt))
    session_messages.append(HumanMessage(content=user_input))

    response = agent_executor.invoke({"messages": session_messages})

    final_msg = response["messages"][-1]
    session_messages.append(final_msg)

    cleaned = clean_text(final_msg.content)

    return cleaned

#a function to generate itinerary based on the user input
def generate_itinerary(source=None, destination=None, budget=None, days=None, food_pref=None, specs=None, adults=1, children=0, travel_date=None, currency="INR"):
    #formatting the query to ensure the agent passes the right passenger counts and dates to the flight tool
    query = f"""
Plan a trip with the following details:

Source: {source}
Destination: {destination}
Travel Date: {travel_date}
Adults: {adults}
Children: {children}
Duration: {days}
Budget: {budget}
Currency: {currency}
Food Preference: {food_pref}
Preferences: {specs}
"""

    session_id = "default_session"

    return run_agent(query, session_id)