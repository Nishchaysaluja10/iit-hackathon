"""
Module: ingestor.py
Description: Handles data ingestion using Pathway.
"""

import pathway as pw

class DataIngestor:
    """
    Responsible for ingesting data from various sources (files, streams) using Pathway.
    """

    def __init__(self, data_dir: str, watch_mode: bool = True):
        """
        Initialize the ingestor.

        Args:
            data_dir (str): Directory containing the data files (books/, csvs/).
            watch_mode (bool): If True, uses Pathway's file watching capabilities.
        """
        self.data_dir = data_dir
        self.watch_mode = watch_mode

    def ingest_books(self) -> pw.Table:
        """
        Ingest text files (novels) from the data directory.

        Returns:
            pw.Table: A Pathway table representing the ingested book content.
                      Columns: [data, modified_at, path, text]
        """
        # Read files from the data directory
        # mode="streaming" allows real-time updates when new files are added
        # format="binary" is required for ParseUnstructured/UnstructuredParser
        files = pw.io.fs.read(
            self.data_dir,
            format="binary",
            mode="streaming" if self.watch_mode else "static",
            with_metadata=True,
        )

        # Decode binary data to text is handled by format="plaintext"
        # We simply return the files table which contains [data, _metadata]
        # This preserves _metadata for VectorStoreServer
        return files

    def ingest_test_csv(self, csv_path: str) -> pw.Table:
        """
        Ingest the test CSV containing character backstories.

        Args:
            csv_path (str): Path to the test CSV file.

        Returns:
            pw.Table: A Pathway table representing the CSV data.
        """
        # Read CSV file
        # Default mode is streaming, but for a potentially static CSV, 'static' might be safer
        # unless we expect the CSV to grow. The existing code passes watch_mode to constructor.
        # Let's assume the CSV might update or just use the same mode policy.
        
        class BackstorySchema(pw.Schema):
            content: str

        table = pw.io.csv.read(
            csv_path,
            mode="streaming" if self.watch_mode else "static",
            schema=BackstorySchema
        )
        # Rename content to backstory to match main.py expectation across files
        return table.select(backstory=pw.this.content)
