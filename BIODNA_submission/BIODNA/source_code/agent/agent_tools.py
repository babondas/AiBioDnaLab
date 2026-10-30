"""The tools the BIODNA agent can use. The LLM decides which one to call.

    search_lab_documents(query)    search by meaning      SOPs, procedures, guidelines
    lookup_table_rows(keyword)     exact word lookup      reference ranges, critical values,
                                                          tubes, fasting, turnaround times
    list_lab_documents()           list loaded files      "Which documents do you have?"

Usage:
    lab_tools = LabTools(vector_store)
    tools = lab_tools.create_tools()
"""
from langchain_core.tools import tool

from source_code.agent.agent_instructions import NOTHING_FOUND_FOR_LLM
from source_code.common.data_models import SearchResult
from source_code.rag_pipeline.step4_vector_store import VectorStore


class LabTools:

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.sources_used: list[SearchResult] = []    # every chunk a tool returned for this question
        self.tools_used: list[str] = []               # the name of every tool called for this question

    def create_tools(self) -> list:
        """Creates the three tools. They are defined here so they can use self.vector_store."""

        @tool
        def search_lab_documents(query: str) -> str:
            """Searches all BIODNA lab documents by meaning and returns the most relevant
            passages with their sources. Use it for procedures, SOPs, safety, guidelines and
            front office questions."""
            self.tools_used.append("search_lab_documents")
            results = self.vector_store.search(query)
            return self._format_for_llm(results)

        @tool
        def lookup_table_rows(keyword: str) -> str:
            """Finds every row in the CSV and Excel tables that contains the keyword exactly.
            Use it for exact values about one test or parameter: reference ranges, critical
            values, tube or container, fasting, turnaround time, price. The keyword should be
            a short test or parameter name, for example 'HbA1c', 'Potassium', 'Lipid Profile'."""
            self.tools_used.append("lookup_table_rows")
            rows = self.vector_store.find_table_rows_containing(keyword)
            return self._format_for_llm(rows)

        @tool
        def list_lab_documents() -> str:
            """Lists the documents currently loaded in BIODNA, with their type and upload time."""
            self.tools_used.append("list_lab_documents")
            documents = self.vector_store.list_documents()
            if len(documents) == 0:
                return "No documents are loaded yet."

            lines = []
            for document in documents:
                lines.append(f"- {document['file_name']} ({document['file_type']}, "
                             f"{document['chunks']} chunks, uploaded {document['uploaded_at']})")
            return "\n".join(lines)

        return [search_lab_documents, lookup_table_rows, list_lab_documents]

    def clear_history(self):
        """Called at the start of every new question."""
        self.sources_used = []
        self.tools_used = []

    def _format_for_llm(self, results: list[SearchResult]) -> str:
        """Writes the found chunks as text, each labelled with its source."""
        if len(results) == 0:
            return NOTHING_FOUND_FOR_LLM

        self.sources_used.extend(results)

        passages = []
        for number, result in enumerate(results, start=1):
            source_label = f"[Source {number}: {result.file_name} ({result.location})]"
            passages.append(source_label + "\n" + result.text)
        return "\n\n".join(passages)