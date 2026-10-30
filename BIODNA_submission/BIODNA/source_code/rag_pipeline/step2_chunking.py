"""RAG step 2: split long pages into smaller overlapping chunks, and add metadata.

    One page (2000 characters)
            |
            v
    Chunk 1: characters    1 - 800
    Chunk 2: characters  700 - 1500     (shares 100 characters with chunk 1)
    Chunk 3: characters 1400 - 2000     (shares 100 characters with chunk 2)

Why: a search should return the one paragraph that answers the question,
not a whole page. The overlap makes sure a sentence cut at the edge of
one chunk still appears whole in the next.

Short text (like one table row) stays as one chunk.

Every chunk also gets metadata: file name, file type, location,
chunk number and upload time. Metadata is not searched by meaning;
it is used to show sources, manage documents and filter results.

Usage:
    chunker = TextChunker()
    chunks = chunker.split_into_chunks(sections, file_name)
"""
from datetime import datetime
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from source_code.common import config
from source_code.common.data_models import Chunk, Section


class TextChunker:

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,          # 800 characters
            chunk_overlap=config.CHUNK_OVERLAP,    # 100 characters
            separators=["\n", ". ", " "],          # try to cut at a new line, then a sentence, then a word
        )

    def split_into_chunks(self, sections: list[Section], file_name: str) -> list[Chunk]:
        """Main method: splits every page into chunks and adds metadata to each chunk."""
        file_type = Path(file_name).suffix.lower().replace(".", "")    # "BIODNA.csv" -> "csv"
        uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M")        # same time for the whole file

        chunks = []
        for section in sections:
            pieces = self.splitter.split_text(section.text)

            for piece in pieces:
                chunks.append(Chunk(
                    text=piece,
                    file_name=file_name,
                    file_type=file_type,
                    location=section.location,
                    chunk_number=len(chunks) + 1,
                    uploaded_at=uploaded_at,
                ))
        return chunks
