import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from backend.vector_tools import search_local_knowledge, web_search
from backend.memory import get_session

load_dotenv()

llm = ChatGroq(
    model_name="openai/gpt-oss-120b",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

tools = [search_local_knowledge, web_search]
agent_executor = create_react_agent(llm, tools)


def clean_text(text):
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"^[\*\-]\s+", "", text, flags=re.MULTILINE)
    text = text.replace("*", "")
    return text


def extract_places(text):
    pattern = r"(?:Place\s*–\s*|Visit\s+|Explore\s+|Stay\s*–\s*|Food\s*–\s*)([A-Z][a-zA-Z0-9\s&\-\(\)]+)"
    matches = re.findall(pattern, text)

    cleaned = list(set([
        m.strip()
        for m in matches
        if len(m.split()) <= 6
    ]))

    return cleaned



def run_agent(user_input: str, session_id: str):
    session_messages = get_session(session_id)

    system_prompt = """
You are a smart Local-First Travel Planner.

RULES:

1. DO NOT include timings.

2. ALWAYS return:
Day 1:
- Place
- Place
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
- No explanations

6. FOOD:
- Respect user preference

BUDGET (MANDATORY):

Budget:
- Per Person: currency based on destination
- Total: currency based on destination

If international:
- Show BOTH currencies
Example:
₹80,000 (~$950 / £750)

If source and destination are have same currency value then it is fine to give only in one currency.
"""

    session_messages.append(SystemMessage(content=system_prompt))
    session_messages.append(HumanMessage(content=user_input))

    response = agent_executor.invoke({"messages": session_messages})

    final_msg = response["messages"][-1]
    session_messages.append(final_msg)

    cleaned = clean_text(final_msg.content)

    return cleaned


def generate_itinerary(source=None, destination=None, budget=None, days=None, food_pref=None, specs=None, travelers=None):
    query = f"""
Plan a trip with the following details:

Source: {source}
Destination: {destination}
Travelers: {travelers}
Duration: {days}
Budget: {budget}
Food Preference: {food_pref}
Preferences: {specs}
"""

    session_id = "default_session"

    return run_agent(query, session_id)