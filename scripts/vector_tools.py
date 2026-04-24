from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

# 1. Initialize Search (Upgraded to return links)
web_search = DuckDuckGoSearchResults()

# 2. Setup Vector DB
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
CHROMA_PATH = "./vector_db/travel_data"
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

@tool
def search_local_knowledge(query: str) -> str:
    """
    Search our local travel database for things to do, 
    historical info, and destination insights.
    """
    results = db.similarity_search(query, k=2)
    # Returns snippets from your cleaned CSVs and Wiki data
    context = "\n---\n".join([res.page_content[:400] for res in results])
    return context