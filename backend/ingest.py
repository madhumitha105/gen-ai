import wikipedia
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

#path to store the vector embedddings
CHROMA_PATH = "./vector_db/travel_data"

def ingest_wikipedia(topics):
    all_docs = []
    
    for topic in topics:
        print(f"Fetching API data for: {topic}")
        try:
            #fetching content using api
            page = wikipedia.page(topic)
            clean_text = page.content
            url = page.url
            
            all_docs.append(Document(
                page_content=clean_text, 
                metadata={"source": url, "hierarchy": "Global/Country"}
            ))
        except Exception as e:
            print(f"Error fetching {topic}: {e}")

    if not all_docs:
        print("No documents fetched.")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(all_docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)
    return db

if __name__ == "__main__":
    #giving the topics so the api can get website
    topics = [
        "Tourism in India",
        "Tourism in Europe",
        "Tourism in Southeast Asia",
        "Tourism in North America",
        "Tourism in the Middle East"
    ]
    ingest_wikipedia(topics)
    print("\nKnowledge Base expanded via API")