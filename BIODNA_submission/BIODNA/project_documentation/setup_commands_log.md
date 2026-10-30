# BIODNA – Setup Commands

## Step 1: Check Python version

```
python --version
```

Result: Python 3.13.14

## Step 2: Create project folders

```
cd C:\Projects\AI
mkdir BIODNA
cd BIODNA
mkdir src documents vector_db sample_data\valid sample_data\invalid docs tests experiments
```

The folders were then renamed to:

```
BIODNA/
├── practice_scripts_for_experiments/
├── project_documentation/
├── sample_documents_for_testing/
│   ├── supported_files/
│   └── unsupported_or_broken_files/
├── self_check_functionality_tests/
├── source_code/
│   └── __init__.py
├── uploaded_documents/
└── vector_database/
```

## Step 3: Create virtual environment

```
cd C:\Projects\AI\BIODNA
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
where python
```

The first line of `where python` must show:

```
C:\Projects\AI\BIODNA\venv\Scripts\python.exe
```

Every time you open a new Command Prompt, run:

```
cd C:\Projects\AI\BIODNA
venv\Scripts\activate
```

In the VS Code PowerShell terminal, activate with:

```
venv\Scripts\Activate.ps1
```

## Step 4: Install packages

Create a file named `requirements.txt` in the main BIODNA folder:

```
--extra-index-url https://download.pytorch.org/whl/cpu
torch
streamlit
langchain-core
langchain-text-splitters
langchain-huggingface
sentence-transformers
chromadb
pypdf
pandas
openpyxl
xlrd
python-dotenv
pytest
truststore
```

Install everything (check `(venv)` is showing first):

```
pip install -r requirements.txt
```

Check it worked:

```
python -c "import torch, chromadb, sentence_transformers, langchain_huggingface, streamlit; print('All good')"
```

Note: the file name must be exactly `requirements.txt`. Turn on File Explorer → View → Show → File name extensions to avoid names like `requirement.txt.txt`.

## Step 5: Hugging Face token and .env

Create a token at huggingface.co → Settings → Access Tokens → Fine-grained, with "Make calls to Inference Providers" ticked.

Create these files in the main BIODNA folder.

`.env`:

```
HF_TOKEN=your_real_token
HF_MODEL=openai/gpt-oss-20b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

`.gitignore`:

```
venv/
.env
__pycache__/
vector_database/*
uploaded_documents/*
```

## Step 6: Test the model

Create the test script `practice_scripts_for_experiments\test_llm.py`, then run:

```
python practice_scripts_for_experiments\test_llm.py
```

Result: logged in, model answered.

## Step 7: Test the embedding model

Create the test script `practice_scripts_for_experiments\test_embeddings.py`, then run:

```
python practice_scripts_for_experiments\test_embeddings.py
```

Result: 384 numbers per embedding. The matching sentence scored 0.649; unrelated sentences scored 0.067 and 0.171.

## Step 8: Sample documents

Good files in `sample_documents_for_testing\supported_files`:

- `BIODNA_SOP_Specimen_Collection_and_Rejection.pdf`
- `BIODNA_SOP_Biomedical_Waste_and_Spill_Handling.pdf`
- `BIODNA_Front_Office_and_Patient_Preparation_Guidelines.txt`
- `BIODNA_Test_Catalog.csv`
- `BIODNA_Reference_Ranges_and_Critical_Values.xlsx`

Bad files in `sample_documents_for_testing\unsupported_or_broken_files` are created by running:

```
python practice_scripts_for_experiments\create_bad_test_files.py
```

Result: 13 bad files created.

## Step 9: Source code structure

```
source_code/
├── __init__.py
├── common/
│   ├── __init__.py
│   ├── config.py              ← settings: folders, models, limits
│   ├── custom_errors.py       ← error classes
│   └── user_messages.py       ← messages shown to users
└── document_reading/
    ├── __init__.py
    ├── document_reader.py     ← main function and flow diagram
    ├── file_checks.py         ← checks 1-3: format, content, size
    └── file_extractors.py     ← step 4: PDF, TXT, CSV, Excel readers
```

Check the settings:

```
python -c "from source_code.common import config; print(config.PROJECT_FOLDER); print(config.HF_MODEL)"
```

Result should be `C:\Projects\AI\BIODNA` and `openai/gpt-oss-20b`.

## Step 10: Document reader

The app calls `validate_and_read_uploaded_file` in `document_reader.py`. It runs the checks in order (format, content, size), then the right reader for the file type.

Quick check on all sample files:

```
python -m practice_scripts_for_experiments.test_document_reader
```

Expected: 5 OK (supported files) and 13 ERROR with friendly messages (broken files).

Note: scripts that import from `source_code` must be run with `python -m` from the BIODNA folder.

## Step 11: Automated tests

Test file: `unit_tests\test_document_reading.py` (unittest style, like C# MSTest).

```
python -m pytest unit_tests -v
```

Result: 20 passed.

Add `.pytest_cache/` to `.gitignore`, and do not include it in the submission zip.

## Step 12: RAG pipeline

```
source_code/rag_pipeline/
├── pipeline_runner.py         ← runs steps 1-4 for one uploaded file
├── step1_data_cleaning.py     ← remove headers, footers, page numbers, extra spaces
├── step2_chunking.py          ← split into 800-character chunks, add metadata
├── step3_embedding.py         ← turn text into 384 numbers (Hugging Face model)
└── step4_vector_store.py      ← store in ChromaDB, search by meaning, exact table lookup
```

Data classes (`Section`, `Chunk`, `SearchResult`, `AgentAnswer`) are in `source_code\common\data_models.py`.

Check chunking:

```
python -m practice_scripts_for_experiments.test_chunking
```

Result: 8, 81, 7, 11 and 28 chunks; none longer than 800 characters.

Check the vector store (fills the `vector_database` folder):

```
python -m practice_scripts_for_experiments.test_vector_store
```

Result: 6 of 6 searches found the right document; the unrelated question returned nothing (relevance threshold 0.30).

## Step 13: Agent

```
source_code/agent/
├── llm_connection.py          ← connects to the Hugging Face LLM
├── agent_instructions.py      ← the rules (system prompt)
├── agent_tools.py             ← 3 tools: search_lab_documents, lookup_table_rows, list_lab_documents
└── lab_agent.py               ← the agent: prompt | model chain and the tool loop
```

Check that the model can call a tool:

```
python -m practice_scripts_for_experiments.test_tool_calling
```

Check the agent:

```
python -m practice_scripts_for_experiments.test_agent
```

Result: 5 of 5 answers correct, each using the right tool; the unrelated question got "I couldn't find this in the BIODNA documents."

## Step 14: Guardrails

```
source_code/guardrails/
├── input_guardrails.py        ← before the LLM: empty, length, no words, prompt injection, diagnosis, personal data
└── output_guardrails.py       ← after the LLM: empty answer, hidden secrets, warning if no tool was used
```

Check them:

```
python -m practice_scripts_for_experiments.test_input_guardrails
python -m practice_scripts_for_experiments.test_output_guardrails
```

Result: input 2 OK and 5 BLOCKED; output checks replace empty answers, hide tokens and warn on answers not from the documents.

Note: never create files inside `__pycache__` folders; Python manages them automatically.

