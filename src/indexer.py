"""
Module: indexer.py
Description: Manages vector indexing using Pathway's LLM XPack.
"""

import pathway as pw
from pathway.xpacks import llm

class HybridIndexer:
    """
    Builds and manages a Hybrid Vector Store (Vector + Keyword) for efficient retrieval.
    """

    def __init__(self, embedder_config: dict = None):
        """
        Initialize the indexer.

        Args:
            embedder_config (dict): Configuration for the embedding model (e.g., LiteLLM/OpenAI).
        """
        self.embedder_config = embedder_config

    def build_index(self, table: pw.Table) -> pw.Table:
        """
        Create a vector index from the ingested text table.

        Args:
            table (pw.Table): Input Pathway table containing text chunks from novels.

        Returns:
            pw.Table: An indexed table ready for ANN search.
        """
        # Create a vector store using Pathway's LLM XPack
        # This automatically handles splitting, embedding, and indexing
        return llm.vector_store(
            table,
            embedder=self.embedder_config,
            # We can rely on default splitter or customize if needed
        )
