from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from backend.flight_data import get_flights as flight_data

web_search = DuckDuckGoSearchResults()

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
CHROMA_PATH = "./vector_db/travel_data"
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

@tool
def get_flights(source: str, destination: str):
    """Get flight options between source and destination"""
    return flight_data(source, destination)

@tool
def search_local_knowledge(query: str) -> str:
    """
    Search our local travel database for things to do, 
    historical info, and destination insights.
    """
    results = db.similarity_search(query, k=2)
    context = "\n---\n".join([res.page_content[:400] for res in results])
    return context