
import pathway as pw
from dotenv import load_dotenv
import os
from src.ingestor import DataIngestor
from src.indexer import HybridIndexer
from src.auditor import NarrativeAuditor

def main():
    load_dotenv()
    
    # 1. Setup
    DATA_DIR = "./data/mini/"
    GOLD_CSV = "./data/gold_standard.csv"
    
    # 2. Ingest
    ingestor = DataIngestor(DATA_DIR)
    books_table = ingestor.ingest_books()
    
    # 3. Index
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    indexer = HybridIndexer(embedder_config={"model": "gemini/text-embedding-004", "api_key": api_key})
    index = indexer.build_index(books_table)
    
    # 4. Audit Claims from Gold Standard
    # Schema of GOLD_CSV: claim, expected
    gold_table = pw.io.csv.read(GOLD_CSV, schema=pw.schema_from_csv(GOLD_CSV), mode="static")
    
    auditor = NarrativeAuditor(
        index_table=index, 
        llm_config={"model": "gemini/gemini-flash-latest", "api_key": api_key}
    )
    
    # We only need the 'claim' column for the auditor
    # The 'expected' column will be used for metric calculation later (preserved if we join? No, let's keep it simple)
    # We will just verify the claims.
    
    # Flattening not needed as claims are already individual rows in gold standard
    
    results = auditor.audit_backstory(gold_table)
    
    # 5. Save Results
    pw.io.csv.write(results, "results/evaluation_results.csv")
    
    print("Evaluation pipeline started. Results will be in 'results/evaluation_results.csv'.")
    pw.run()

if __name__ == "__main__":
    main()
