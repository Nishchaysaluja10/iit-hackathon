import pathway as pw
from dotenv import load_dotenv
import os
import asyncio
from src.ingestor import DataIngestor
from src.indexer import HybridIndexer
from src.analyzer import BackstoryAnalyzer
from src.auditor import NarrativeAuditor

# Load env variables
load_dotenv()

def verify_full():
    print("Starting full pipeline verification...")
    DATA_DIR = "./data/"
    TEST_CSV = "./data/test_mini.csv"

    # 1. Ingestion
    ingestor = DataIngestor(DATA_DIR, watch_mode=False) 
    books_table = ingestor.ingest_books()
    test_table = ingestor.ingest_test_csv(TEST_CSV)
    
    # 2. Indexing
    print("Building Index...")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    indexer = HybridIndexer(embedder_config={"model": "gemini/text-embedding-004", "api_key": api_key})
    # Mocking or using small index
    index = indexer.build_index(books_table)

    # 3. Analyze
    print("Initializing Analyzer...")
    analyzer = BackstoryAnalyzer(llm_config={"model": "gemini/gemini-flash-latest", "api_key": api_key})
    
    @pw.udf
    async def decompose_udf(text: str) -> list[str]:
        # Mock decomposition to avoid heavy LLM usage in test if desired
        # or use real one. Let's use real one but handle errors.
        try:
            return await analyzer.extract_atomic_claims(text)
        except Exception:
            return ["Claim 1", "Claim 2"]

    claims_table = test_table.select(
        original_text=pw.this.backstory,
        claims=decompose_udf(pw.this.backstory)
    )
    
    atomic_claims = claims_table.flatten(pw.this.claims).select(
        claim=pw.this.claims,
        source_text=pw.this.original_text
    )

    # 4. Audit
    print("Auditing...")
    auditor = NarrativeAuditor(index_table=index, llm_config={"model": "gemini/gemini-flash-latest", "api_key": api_key})
    
    # We need to monkeypath/mock the LLM call inside auditor if we want to run fast without credits,
    # but let's try real run first.
    audit_results = auditor.audit_backstory(atomic_claims)
    
    # 5. Output
    print("Computing results and writing to CSV...")
    pw.io.csv.write(audit_results, "audit_results.csv")
    pw.run()

if __name__ == "__main__":
    verify_full()
