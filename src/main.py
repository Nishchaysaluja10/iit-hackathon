"""
Module: main.py
Description: Orchestrator for the Narrative Consistency Verification system.
"""

import pathway as pw
from dotenv import load_dotenv
import os

# Load environment variables (e.g., OPENAI_API_KEY)
load_dotenv()
from src.ingestor import DataIngestor
from src.indexer import HybridIndexer
from src.analyzer import BackstoryAnalyzer
from src.auditor import NarrativeAuditor

def main():
    """
    Main execution loop:
    1. Load Data (Books & CSV)
    2. Index Books
    3. Decompose Backstories
    4. Audit Claims
    5. Save Results
    """
    # 1. Configuration
    DATA_DIR = "./data/mini/"
    TEST_CSV = "./data/external/Dataset/train.csv"

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--reindex", action="store_true", help="Clear existing index before ingestion")
    args = parser.parse_args()
    if args.reindex:
        import shutil, os
        index_dir = os.path.join(os.getcwd(), "data", "index")
        if os.path.isdir(index_dir):
            shutil.rmtree(index_dir)
            print(f"Removed existing index directory: {index_dir}")
        else:
            print("No existing index directory to remove.")
    
    # 2. Ingestion
    ingestor = DataIngestor(DATA_DIR)
    books_table = ingestor.ingest_books()
    external_ingestor = DataIngestor("./data/external/Dataset/Books")
    external_table = external_ingestor.ingest_books()
    # Ensure universes are disjoint before concatenation
    books_table = books_table.promise_universes_are_disjoint(external_table)
    combined_table = books_table.concat(external_table)
    
    # 3. Indexing
    # ingestor.ingest_books()
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    indexer = HybridIndexer(embedder_config={
        "model": "gemini/text-embedding-004", 
        "api_key": api_key
    }) 
    index = indexer.build_index(combined_table)
    
    # 4. Processing Pipeline
    # A. Ingest Backstories
    test_table = ingestor.ingest_test_csv(TEST_CSV)
    
    # B. Analyze (Decompose) Backstories
    # Initialize Analyzer
    # using gemini-flash-latest explicitly to avoid version issues
    analyzer = BackstoryAnalyzer(llm_config={"model": "gemini/gemini-flash-latest", "api_key": api_key})
    
    # Define UDF for Pathway
    @pw.udf
    async def decompose_udf(text: str) -> list[str]:
        return await analyzer.extract_atomic_claims(text)

    # Apply decomposition
    claims_table = test_table.select(
        original_text=pw.this.backstory,
        claims=decompose_udf(pw.this.backstory)
    )
    
    # Flatten/Explode claims so each claim is a row
    atomic_claims = claims_table.flatten(pw.this.claims).select(
        claim=pw.this.claims,
        source_text=pw.this.original_text
    )

    # C. Audit Claims
    auditor = NarrativeAuditor(
        index_table=index, 
        llm_config={"model": "gemini/gemini-flash-latest", "api_key": api_key}
    )
    audit_results = auditor.audit_backstory(atomic_claims)
    
    # 5. Output
    # Write results to CSV
    pw.io.csv.write(audit_results, "audit_results.csv")
    
    print("Pipeline defined. Starting Pathway...")
    pw.run()

if __name__ == "__main__":
    main()
