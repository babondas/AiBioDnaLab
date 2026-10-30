"""RAG step 3: turn text into embeddings (lists of 384 numbers that capture meaning).

    "Which tube is used for HbA1c?"  -->  [0.021, -0.113, 0.067, ... 384 numbers]

Texts with similar meaning get similar numbers, even if they use different words.

The model runs on Hugging Face's servers (Inference API), not on this computer:
nothing is downloaded and PyTorch is not needed. Each call needs internet and HF_TOKEN.

Usage:
    embedding_model = EmbeddingModel()
    numbers = embedding_model.embed_question("Which tube is used for HbA1c?")
"""
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from source_code.common import config


class EmbeddingModel:
    """Connects once to the Hugging Face embedding service, then reuses the connection."""

    def __init__(self):
        self.model = HuggingFaceEndpointEmbeddings(
            model=config.EMBEDDING_MODEL,
            huggingfacehub_api_token=config.HF_TOKEN,
            provider="hf-inference",              # Hugging Face's own inference servers
        )

    def embed_chunks(self, texts: list[str]) -> list[list[float]]:
        """Many texts, used when storing a document. Sent in small batches to keep each request small."""
        embeddings = []
        for start in range(0, len(texts), config.EMBEDDING_BATCH_SIZE):
            batch = texts[start:start + config.EMBEDDING_BATCH_SIZE]
            embeddings.extend(self.model.embed_documents(batch))
        return embeddings

    def embed_question(self, question: str) -> list[float]:
        """One text, used when searching."""
        return self.model.embed_query(question)
