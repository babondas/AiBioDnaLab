"""All BIODNA settings in one place."""
import truststore
truststore.inject_into_ssl()   # use the Windows certificate store (office networks)

import os
from pathlib import Path
from dotenv import load_dotenv

# ---- Folders ----
PROJECT_FOLDER = Path(__file__).resolve().parent.parent.parent   # common -> source_code -> BIODNA
UPLOADED_DOCUMENTS_FOLDER = PROJECT_FOLDER / "uploaded_documents"
VECTOR_DATABASE_FOLDER = PROJECT_FOLDER / "vector_database"

load_dotenv(PROJECT_FOLDER / ".env")

# ---- Hugging Face models ----
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = os.getenv("HF_MODEL", "openai/gpt-oss-20b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_BATCH_SIZE = 32         # texts sent to the embedding service per request

# ---- Upload rules ----
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".csv", ".xlsx"}
MAX_FILE_SIZE_MB = 10

# ---- Vector database (RAG) ----
CHUNK_SIZE = 800                 # characters per chunk
CHUNK_OVERLAP = 100              # characters shared between neighbouring chunks
TOP_K_RESULTS = 4                # how many chunks a search returns
MIN_RELEVANCE_SCORE = 0.30       # chunks scoring below this are treated as "not relevant"
MAX_TABLE_ROWS_RETURNED = 10     # most table rows an exact lookup returns

# ---- Agent (LLM) ----
LLM_TEMPERATURE = 0.1            # low = consistent, factual answers (fewer hallucinations)
LLM_MAX_TOKENS = 1024            # room for the model's thinking plus the answer
MAX_AGENT_STEPS = 3              # how many times the agent may search before it must answer
VALIDATE_ANSWERS = True          # False = skip the Answer Validator (saves one LLM call per question)

# ---- Guardrails ----
MIN_QUESTION_LENGTH = 3          # characters
MAX_QUESTION_LENGTH = 500        # characters