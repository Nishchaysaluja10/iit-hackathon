"""
Module: main.py
Description: Orchestrator for the Narrative Consistency Verification system.
"""

import pathway as pw
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
    indexer = HybridIndexer()
    index = indexer.build_index(books_table)

    # 4. Processing Pipeline
    # Define Pathway computation graph here
    # Use pw.apply to run analyzer and auditor logic

    # 5. Output
    # pw.io.csv.write(result_table, "output.csv")
    
    # pw.run() # Start the pipeline

if __name__ == "__main__":
    main()
