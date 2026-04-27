import os
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

INPUT_DIRECTORY = r"data/static_rag" 
CHROMA_PATH = "./vector_db/travel_data"

#hugging face embeddings to convert txt to num
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

#a function to ingest all csv
def ingest_all_csvs():
    if not os.path.exists(INPUT_DIRECTORY):
        print(f"Error: The path {INPUT_DIRECTORY} does not exist.")
        return

    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
    
    csv_files = [f for f in os.listdir(INPUT_DIRECTORY) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return

    for filename in csv_files:
        file_path = os.path.join(INPUT_DIRECTORY, filename)
        print(f"Processing: {filename}...")
        
        try:
            df = pd.read_csv(file_path)
            df = df.dropna(how='all') #dropping the rows if all values are null
            df = df.fillna("Unknown") #filling 'unknown' value in empty cells
            df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
            df = df.drop_duplicates()

            documents = []
            for _, row in df.iterrows():
                content = " | ".join([f"{col}: {val}" for col, val in row.items()]) #converts csv to | seperated values as string (within quotes)
                doc = Document(
                    page_content=content, 
                    metadata={"source": filename, "type": "static_data"} #attaching file name as the metadata, so llm can quote from which csv it got that info
                )
                documents.append(doc)
            
            if documents:
                db.add_documents(documents)
                print(f"Done: Cleaned and added {len(documents)} records from {filename}") #adding the cleaned doc to vectorDB
            else:
                print(f"Skipping {filename}: No valid data found after cleaning.")
            
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    print("\n--- All cleaned static data has been merged into the Vector DB ---")

if __name__ == "__main__":
    ingest_all_csvs()