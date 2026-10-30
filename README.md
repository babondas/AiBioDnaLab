# 🧬 BIODNA – Pathology Lab Knowledge Assistant

BIODNA is a chatbot for pathology lab staff. You upload the lab's documents (PDF, TXT, CSV or Excel) and ask questions in plain English. It answers only from those documents and shows the source.

⚠️ BIODNA does **not** diagnose or suggest treatment. All sample data is made up.

Full details: [`project_documentation/BIODNA_Project_Documentation.md`](project_documentation/BIODNA_Project_Documentation.md)

---

## How it works

### Adding a document (RAG)

```
  Your file
      │
      ▼
  Check the file ──► wrong or broken? ──► error message
      │
      ▼
  Read → Clean → Cut into chunks → Turn into numbers (embeddings)
      │
      ▼
  Save in ChromaDB (vector database)
```

### Answering a question (agents + RAG)

```
  Your question
      │
      ▼
  Safety check ──► unsafe? ──► blocked
      │
      ▼
  LAB AGENT (agent 1)
    picks a tool → searches ChromaDB → writes the answer from what it found
      │
      ▼
  ANSWER VALIDATOR (agent 2)
    checks the answer against the documents → ✓ or ⚠️
      │
      ▼
  Answer + sources on screen
```

---

## How to run it (Windows)

You need **Python 3.11 or newer** and **internet**.

**1. Open a terminal in the `BIODNA` folder.**

**2. Create and turn on a virtual environment:**

```
python -m venv venv
venv\Scripts\activate
```

**3. Install the packages:**

```
pip install -r requirements.txt
```

**4. Create the `.env` file.** A working Hugging Face token is already included in `.env.example`, so just copy it:

```
copy .env.example .env
```

To use your own token instead, open `.env` and replace the `HF_TOKEN` value. Tokens are created at https://huggingface.co/settings/tokens and need the "Make calls to Inference Providers" permission.

**5. Start the app:**

```
streamlit run app.py
```

It opens at **http://localhost:8501**.

**6. In the sidebar, click "Load sample documents", then ask a question.**

The vector database starts empty, so this step is needed on the first run.

---

## Questions to try

| Ask | Expected |
|---|---|
| Which tube is used for HbA1c? | Lavender top (K2 EDTA), with source |
| What is the critical value for potassium? | 2.8 and 6.2 mmol/L |
| Do I have diabetes if my HbA1c is 7? | Blocked |
| Who won the cricket match yesterday? | "I couldn't find this in the BIODNA documents." |

To test error handling, upload files from `sample_documents_for_testing\unsupported_or_broken_files`.

---

## Problems?

| Problem | Fix |
|---|---|
| PowerShell: "running scripts is disabled" | Use Command Prompt (`cmd`) instead |
| Token error | Check `HF_TOKEN` in `.env`. The token needs "Make calls to Inference Providers" |
| "Free credit used up" | Use another Hugging Face token |
| "Port 8501 is not available" | The app is already running. Close the other terminal and try again |
| App keeps loading on an office network | Add `HTTPS_PROXY=http://<proxy address>` to `.env` |
