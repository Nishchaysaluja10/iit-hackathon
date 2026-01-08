import pathway as pw
from dotenv import load_dotenv
import os
from src.ingestor import DataIngestor
from src.indexer import HybridIndexer

# Load env variables
load_dotenv()

def verify():
    print("Starting verification...")
    DATA_DIR = "./data/mini/"
    
    # 1. Ingest
    print("Ingesting data...")
    ingestor = DataIngestor(DATA_DIR, watch_mode=False) 
    books_table = ingestor.ingest_books()
    
    # 2. Index
    print("Building index...")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    # text-embedding-004 works
    indexer = HybridIndexer(embedder_config={"model": "gemini/text-embedding-004", "api_key": api_key})
    
    index = indexer.build_index(books_table)
    
    # 3. Query
    print("Preparing query...")
    # Create a simple query table
    # retrieve_query expects: query, k, filepath_globpattern, metadata_filter
    import pandas as pd
    query_df = pd.DataFrame([
        {
            "query": "What is the story about?",
            "k": 3,
            "filepath_globpattern": "*",
            "metadata_filter": None
        }
    ])
    query_table = pw.debug.table_from_pandas(query_df)
    
    print("Running retrieval...")
    # We must use retrieve_query if available
    try:
        results = index.retrieve_query(query_table)
        print("Computing and printing results...")
        pw.debug.compute_and_print(results)
    except Exception as e:
        print(f"Retrieval failed: {e}")
        # Print index just in case
        pw.debug.compute_and_print(index, limit=2)

if __name__ == "__main__":
    verify()
