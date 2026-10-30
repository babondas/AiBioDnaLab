"""RAG step 4: store chunks in ChromaDB and find the ones closest in meaning to a question.

    Storing:    chunk text + embedding + metadata --> ChromaDB (saved in the vector_database folder)
    Searching:  question embedding --> ChromaDB finds closest chunks --> keep only relevant ones

Score = cosine similarity: 1.0 = same meaning, 0.0 = unrelated.

Usage:
    vector_store = VectorStore(EmbeddingModel())
    vector_store.add_chunks(chunks)
    results = vector_store.search("Which tube is used for HbA1c?")
"""
import chromadb
from chromadb.config import Settings

from source_code.common import config
from source_code.common.data_models import Chunk, SearchResult
from source_code.rag_pipeline.step3_embedding import EmbeddingModel

COLLECTION_NAME = "biodna_documents"


class VectorStore:
    """Opened once when the app starts, then reused for every upload and question."""

    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model

        # Open (or create) the database inside the vector_database folder
        client = chromadb.PersistentClient(
            path=str(config.VECTOR_DATABASE_FOLDER),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},     # compare by meaning (cosine similarity)
        )

    # --------------------------------------------------------------
    # Storing and removing documents
    # --------------------------------------------------------------
    def add_chunks(self, chunks: list[Chunk]) -> int:
        """Stores the chunks of one file. Uploading the same file again replaces the old copy."""
        file_name = chunks[0].file_name
        self.remove_document(file_name)

        ids = []
        texts = []
        metadatas = []
        for chunk in chunks:
            ids.append(f"{chunk.file_name}::{chunk.chunk_number}")
            texts.append(chunk.text)
            metadatas.append({
                "file_name": chunk.file_name,
                "file_type": chunk.file_type,
                "location": chunk.location,
                "chunk_number": chunk.chunk_number,
                "uploaded_at": chunk.uploaded_at,
            })

        embeddings = self.embedding_model.embed_chunks(texts)
        self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
        return len(chunks)

    def remove_document(self, file_name: str):
        self.collection.delete(where={"file_name": file_name})

    def list_documents(self) -> list[dict]:
        """Returns one entry per stored file: name, type, upload time and number of chunks."""
        stored = self.collection.get(include=["metadatas"])

        documents = {}
        for metadata in stored["metadatas"]:
            name = metadata["file_name"]
            if name not in documents:
                documents[name] = {
                    "file_name": name,
                    "file_type": metadata["file_type"],
                    "uploaded_at": metadata["uploaded_at"],
                    "chunks": 0,
                }
            documents[name]["chunks"] += 1
        return list(documents.values())

    # --------------------------------------------------------------
    # Exact lookup in tables (CSV and Excel rows)
    # --------------------------------------------------------------
    def find_table_rows_containing(self, keyword: str) -> list[SearchResult]:
        """Returns table rows whose text contains the keyword (not case-sensitive)."""
        stored = self.collection.get(
            where={"file_type": {"$in": ["csv", "xlsx"]}},
            include=["documents", "metadatas"],
        )

        matching_rows = []
        for text, metadata in zip(stored["documents"], stored["metadatas"]):
            if keyword.lower() in text.lower():
                matching_rows.append(SearchResult(
                    text=text,
                    file_name=metadata["file_name"],
                    file_type=metadata["file_type"],
                    location=metadata["location"],
                    chunk_number=metadata["chunk_number"],
                    uploaded_at=metadata["uploaded_at"],
                    score=1.0,                       # exact match
                ))
        return matching_rows[:config.MAX_TABLE_ROWS_RETURNED]

    # --------------------------------------------------------------
    # Searching by meaning
    # --------------------------------------------------------------
    def search(self, question: str) -> list[SearchResult]:
        """Returns the most relevant chunks for a question, best first.
        Chunks below MIN_RELEVANCE_SCORE are dropped, so an unrelated question returns []."""
        if self.collection.count() == 0:
            return []

        question_embedding = self.embedding_model.embed_question(question)
        found = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=min(config.TOP_K_RESULTS, self.collection.count()),
        )

        results = []
        for text, metadata, distance in zip(found["documents"][0], found["metadatas"][0], found["distances"][0]):
            score = 1 - distance                    # Chroma returns distance; convert to similarity
            if score >= config.MIN_RELEVANCE_SCORE:
                results.append(SearchResult(
                    text=text,
                    file_name=metadata["file_name"],
                    file_type=metadata["file_type"],
                    location=metadata["location"],
                    chunk_number=metadata["chunk_number"],
                    uploaded_at=metadata["uploaded_at"],
                    score=round(score, 3),
                ))
        return results
