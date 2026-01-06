import pathway as pw
from src.ingestor import DataIngestor
import os
from dotenv import load_dotenv
import litellm

load_dotenv()

# Define a simple splitter as a UDF
@pw.udf
def simple_split(text: str) -> list[str]:
    # Crude split by words for demo purposes to avoid importing heavy NLP libs
    words = text.split()
    chunks = []
    chunk_size = 50
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

# Define an embedding function using LiteLLM
@pw.udf
def get_embedding(text: str) -> list[float]:
    if not text:
        return []
    try:
        response = litellm.embedding(model="text-embedding-3-small", input=[text])
        return response['data'][0]['embedding']
    except Exception as e:
        return []

def debug_pipeline():
    # 1. Ingest
    print("Ingesting data...")
    data_dir = "./data/"
    # We create a simple ingestion table
    files = pw.io.fs.read(data_dir, format="plaintext", mode="static", with_metadata=True)
    documents = files.select(text=pw.this.data)

    # 2. Split (Flatten the list of chunks)
    print("Splitting into chunks...")
    chunks = documents.select(chunk=simple_split(pw.this.text)).flatten(pw.this.chunk)

    # 3. Embed
    print("Generating embeddings...")
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment.")
        return

    embeddings = chunks.select(
        text=pw.this.chunk,
        vector=get_embedding(pw.this.chunk)
    )

    # 4. Print results
    print("Computing and printing first 2 rows of embeddings...")
    pw.debug.compute_and_print(embeddings)

if __name__ == "__main__":
    debug_pipeline()
