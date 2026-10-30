"""Runs the full RAG pipeline for one uploaded file.

    Uploaded file
         |
    Read the file                  document_reading/document_reader.py
         |
    Step 1: clean                  step1_data_cleaning.py
         |
    Step 2: chunk + metadata       step2_chunking.py
         |
    Step 3 + 4: embed and store    step3_embedding.py + step4_vector_store.py
         |
    Ready to search

Usage:
    vector_store = VectorStore(EmbeddingModel())
    number_of_chunks = add_uploaded_file_to_knowledge_base(vector_store, file_name, file_bytes)
"""
from source_code.document_reading.document_reader import validate_and_read_uploaded_file
from source_code.rag_pipeline.step1_data_cleaning import DataCleaner
from source_code.rag_pipeline.step2_chunking import TextChunker
from source_code.rag_pipeline.step4_vector_store import VectorStore


def add_uploaded_file_to_knowledge_base(vector_store: VectorStore, file_name: str, file_bytes: bytes) -> int:
    """Returns the number of chunks stored. Raises FileReadingError for bad files."""
    sections = validate_and_read_uploaded_file(file_name, file_bytes)
    sections = DataCleaner().clean_sections(sections)
    chunks = TextChunker().split_into_chunks(sections, file_name)
    return vector_store.add_chunks(chunks)
