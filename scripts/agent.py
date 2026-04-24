import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from scripts.vector_tools import search_local_knowledge, web_search

load_dotenv()

llm = ChatGroq(
    model_name="llama-3.1-8b-instant", 
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

tools = [search_local_knowledge, web_search]

# IGNORE ANY YELLOW SQUIGGLY LINES UNDER THIS. IT IS THE CORRECT FUNCTION.
agent_executor = create_react_agent(llm, tools)

def generate_itinerary(source, destination, budget, days, food_pref, specs, travelers):
    dest_str = destination if destination else "Recommend a destination from the Knowledge Base"
    
    query = f"""
    Source: {source}
    Destination: {dest_str}
    Travelers: {travelers}
    Duration: {days} days
    Total Budget: {budget}
    Food Preference: {food_pref}
    Specifications: {specs}
    """
    
    system_prompt = f"""You are a 'Local-First' Travel Agent.
    
    1. PRIORITIZE KNOWLEDGE BASE: Use 'search_local_knowledge' to decide the destination, historical spots, and the daily plan.
    2. WEB SEARCH FOR LINKS: Use 'web_search' ONLY after the plan is built to find real, clickable links for Accommodations and Restaurants.
    3. LOGISTICS: Plan specifically for {travelers}. Calculate the per-person daily budget from the total: {budget}.
    4. DIETARY: Every food suggestion must strictly be {food_pref}.
    5. OUTPUT: Provide a professional itinerary. For every stay and restaurant, you MUST provide a markdown link: [Name](URL)."""

    inputs = {"messages": [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]}
    
    response = agent_executor.invoke(inputs)
    return response["messages"][-1].content