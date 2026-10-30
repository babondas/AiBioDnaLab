"""BIODNA - Pathology Lab Knowledge Assistant.

Run from the BIODNA folder:
    streamlit run app.py

    Sidebar:  upload documents, load the sample documents, see and remove loaded documents
    Main:     chat with BIODNA; every answer shows its sources
"""
from __future__ import annotations      # lets type hints name classes that are imported later

import logging
from typing import TYPE_CHECKING

import streamlit as st

from source_code.common import config
from source_code.common import user_messages as messages
from source_code.common.custom_errors import FileReadingError
from source_code.common.error_explainer import explain_error

# The heavy libraries (PyTorch, LangChain, ChromaDB) are imported inside the functions
# that need them, so the page appears straight away instead of staying blank.
if TYPE_CHECKING:
    from source_code.agent.safe_lab_agent import SafeLabAgent
    from source_code.rag_pipeline.step4_vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
SAMPLE_DOCUMENTS_FOLDER = config.PROJECT_FOLDER / "sample_documents_for_testing" / "supported_files"

st.set_page_config(page_title="BIODNA", page_icon="🧬", layout="wide")


# ===================================================================
# Load once: the embedding model, the vector database and the agent
# (st.cache_resource keeps them in memory, so they are not reloaded on every click)
# ===================================================================
@st.cache_resource(show_spinner=False)
def load_vector_store() -> VectorStore:
    from source_code.rag_pipeline.step3_embedding import EmbeddingModel
    from source_code.rag_pipeline.step4_vector_store import VectorStore
    return VectorStore(EmbeddingModel())


@st.cache_resource(show_spinner=False)
def load_agent(_vector_store: VectorStore) -> SafeLabAgent:
    from source_code.agent.safe_lab_agent import SafeLabAgent
    return SafeLabAgent(_vector_store)


# ===================================================================
# Adding documents
# ===================================================================
def add_file(vector_store: VectorStore, file_name: str, file_bytes: bytes, save_copy: bool) -> bool:
    """Runs one file through the RAG pipeline. Shows the result and returns True if it was added."""
    from source_code.rag_pipeline.pipeline_runner import add_uploaded_file_to_knowledge_base
    try:
        chunk_count = add_uploaded_file_to_knowledge_base(vector_store, file_name, file_bytes)
    except FileReadingError as error:
        st.error(f"**{file_name}**: {error}")
        return False
    except Exception as error:
        logging.exception("Unexpected error while adding %s", file_name)
        st.error(f"**{file_name}**: {explain_error(error)}")
        return False

    if save_copy:
        (config.UPLOADED_DOCUMENTS_FOLDER / file_name).write_bytes(file_bytes)
    st.success(f"**{file_name}**: added ({chunk_count} chunks)")
    return True


def add_files_with_progress(vector_store: VectorStore, files: list[tuple[str, bytes]], save_copy: bool):
    """Adds several files, showing a status box in the sidebar while it works.

    files is a list of (file_name, file_bytes) pairs.
    """
    total = len(files)
    with st.sidebar.status(f"Adding {total} document(s)...", expanded=True) as status_box:
        added = 0
        for number, (file_name, file_bytes) in enumerate(files, start=1):
            st.write(f"{number}/{total} · {file_name}")
            if add_file(vector_store, file_name, file_bytes, save_copy):
                added += 1

        if added == total:
            status_box.update(label=f"Added {added} of {total} document(s)", state="complete")
        else:
            status_box.update(label=f"Added {added} of {total} document(s), see errors below", state="error")


def show_upload_section(vector_store: VectorStore):
    st.sidebar.header("📤 Upload documents")
    uploaded_files = st.sidebar.file_uploader(
        "PDF, TXT, CSV or Excel (max 10 MB each)",
        accept_multiple_files=True,           # no 'type' filter: BIODNA explains unsupported files itself
    )
    if st.sidebar.button("Add to knowledge base", use_container_width=True):
        if not uploaded_files:
            st.sidebar.warning(messages.APP_NO_FILES_CHOSEN)
        else:
            files = [(uploaded_file.name, uploaded_file.getvalue()) for uploaded_file in uploaded_files]
            add_files_with_progress(vector_store, files, save_copy=True)

    st.sidebar.header("📚 Sample documents")
    if st.sidebar.button("Load sample documents", use_container_width=True):
        files = [(sample_file.name, sample_file.read_bytes()) for sample_file in sorted(SAMPLE_DOCUMENTS_FOLDER.iterdir())]
        add_files_with_progress(vector_store, files, save_copy=False)


def show_document_list(vector_store: VectorStore):
    st.sidebar.header("📄 Loaded documents")
    documents = vector_store.list_documents()
    if len(documents) == 0:
        st.sidebar.caption("None yet.")
        return

    for document in documents:
        name_column, button_column = st.sidebar.columns([5, 1])
        name_column.markdown(f"**{document['file_name']}**  \n"
                             f"{document['file_type'].upper()} · {document['chunks']} chunks · {document['uploaded_at']}")
        if button_column.button("🗑", key=f"remove_{document['file_name']}", help="Remove this document"):
            vector_store.remove_document(document["file_name"])
            st.rerun()


# ===================================================================
# Chat
# ===================================================================
def show_message(message: dict):
    """Shows one chat message, with its warning and sources if it has them."""
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

        if message.get("validated"):
            st.caption(messages.APP_ANSWER_VALIDATED)

        if message.get("warning"):
            st.warning(message["warning"])

        sources = message.get("sources", [])
        if sources:
            with st.expander(f"Sources ({len(sources)})"):
                for source in sources:
                    st.markdown(f"**{source.file_name}** · {source.location} · score {source.score}")
                    st.code(source.text, language=None, wrap_lines=True)


def show_chat(vector_store: VectorStore, agent: SafeLabAgent):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        show_message(message)

    question = st.chat_input("Ask a question about the lab...")
    if not question:
        return

    user_message = {"role": "user", "text": question}
    st.session_state.chat_history.append(user_message)
    show_message(user_message)

    if len(vector_store.list_documents()) == 0:
        reply = {"role": "assistant", "text": messages.APP_NO_DOCUMENTS}
    else:
        with st.spinner("BIODNA is looking through the documents..."):
            answer = agent.ask(question)
        reply = {"role": "assistant", "text": answer.text, "sources": answer.sources,
                 "warning": answer.warning, "validated": answer.validated}

    st.session_state.chat_history.append(reply)
    show_message(reply)


# ===================================================================
# The page
# ===================================================================
def main():
    st.title("🧬 BIODNA")
    st.caption("Pathology Lab Knowledge Assistant · " + messages.APP_DISCLAIMER)

    if config.HF_TOKEN == "":
        st.error("HF_TOKEN is missing. Add your Hugging Face token to the .env file and restart the app.")
        st.stop()

    # Show a loader in the main area AND in the sidebar until everything is ready
    with st.spinner(messages.APP_STARTING):
        with st.sidebar:
            with st.spinner(messages.APP_SIDEBAR_LOADING):
                vector_store = load_vector_store()
                agent = load_agent(vector_store)

    show_upload_section(vector_store)
    show_document_list(vector_store)
    show_chat(vector_store, agent)


main()
