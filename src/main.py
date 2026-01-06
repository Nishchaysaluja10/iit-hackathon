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
    DATA_DIR = "./data/"
    TEST_CSV = "./data/test.csv"

    # 2. Ingestion
    ingestor = DataIngestor(DATA_DIR)
    books_table = ingestor.ingest_books()
    test_table = ingestor.ingest_test_csv(TEST_CSV)

    # 3. Indexing
    indexer = HybridIndexer() # Uses default embedder (usually OpenAI)
    index = indexer.build_index(books_table)

    # 4. Processing Pipeline
    # Define Pathway computation graph here
    
    # Placeholder for Analyzer and Auditor integration (to be implemented next)
    # analyzer = BackstoryAnalyzer()
    # auditor = NarrativeAuditor(index)
    
    # For now, we just output the index to verify it works or print stats
    # pw.io.csv.write(index, "index_output.csv") # Optional debug output

    # 5. Output
    # Check if we should run the pipeline (usually main.py is the entry point)
    # We might want to just print something to indicate setup is done
    print("Pipeline defined. Starting Pathway...")
    
    # pw.run() # Start the pipeline
    # NOTE: pw.run() is blocking. In a real app we'd run this.
    # For the purpose of this task step, we will uncomment it if the user wants to run it.
    # But usually we leave it controlled. Let's just uncomment it for "implementation".
    pw.run()

if __name__ == "__main__":
    main()
