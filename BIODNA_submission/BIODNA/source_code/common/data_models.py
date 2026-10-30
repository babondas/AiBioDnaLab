"""The data shapes used across BIODNA (like small C# classes or records)."""
from dataclasses import dataclass, field


@dataclass
class Section:
    """One piece of a document as it was read: a PDF page, the TXT text, or a table row."""
    text: str           # e.g. "HbA1c uses a lavender tube."
    location: str       # e.g. "page 3", "full text", "row 5", "sheet 'Haematology' row 2"


@dataclass
class Chunk:
    """A small piece of a section, plus metadata, ready to be embedded and stored."""
    text: str           # the text that is searched by meaning
    file_name: str      # e.g. "BIODNA_Test_Catalog.csv"
    file_type: str      # e.g. "csv", "pdf", "txt", "xlsx"
    location: str       # e.g. "row 5", "page 3"
    chunk_number: int   # 1, 2, 3 ... order of the chunk inside its file
    uploaded_at: str    # e.g. "2026-10-02 14:30"


@dataclass
class SearchResult:
    """A chunk found by a search, with its relevance score."""
    text: str
    file_name: str
    file_type: str
    location: str
    chunk_number: int
    uploaded_at: str
    score: float        # 1.0 = same meaning, 0.0 = unrelated


@dataclass
class AgentAnswer:
    """The agent's reply to one question."""
    text: str                                              # the answer shown to the user
    sources: list[SearchResult]                            # the chunks the answer is based on
    tools_used: list[str] = field(default_factory=list)    # e.g. ["lookup_table_rows"]
    warning: str = ""                                      # set by the guardrails or the validator, if needed
    validated: bool = False                                # True when the Answer Validator confirmed it