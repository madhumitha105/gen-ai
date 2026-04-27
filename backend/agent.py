import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from backend.vector_tools import search_local_knowledge, web_search
from backend.flight_data import get_flights
from backend.memory import get_session

load_dotenv()

#choosing the LLM
llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    groq_api_key=os.getenv("RAPID_API_KEY"),
    temperature=0
)

#using local DB for planning, web search for links and get_flights for flight details
tools = [search_local_knowledge, web_search, get_flights]
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
You are a smart Local-First Travel Planner.

RULES:

1. DO NOT include timings.

2. ALWAYS return:
Day 1:
- Places to be visited
- Food
- Stay

3. LINKS:
- generate clickable links for user and then give a one liner description about that place
- generate clean place names

4. PRIORITY:
- Use local knowledge tool for planning

5. STYLE:
- Clean bullets
- No paragraphs

6. FOOD:
- Respect user preference

7. BUDGET (MANDATORY):

Budget:
- Per Person: currency based on destination
- Total: currency based on destination

If international:
- Show BOTH currencies
Example:
₹80,000 (~$950 / £750)

If source and destination are have same currency value then it is fine to give only in one currency.

FLIGHTS:

- ALWAYS use get_flights tool when source and destination are different cities/countries
- Use the specific travel date, number of adults, and children provided in the query.
- Show 2-3 flight options
- Include airline, price, duration

Format:

Flights:
- Airline | Price | Duration
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