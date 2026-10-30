from pathlib import Path

from source_code.document_reading.document_reader import validate_and_read_uploaded_file
from source_code.rag_pipeline.step1_data_cleaning import DataCleaner
from source_code.rag_pipeline.step2_chunking import TextChunker

cleaner = DataCleaner()
chunker = TextChunker()

for file in sorted(Path("sample_documents_for_testing/supported_files").iterdir()):
    sections = validate_and_read_uploaded_file(file.name, file.read_bytes())
    sections = cleaner.clean_sections(sections)
    chunks = chunker.split_into_chunks(sections, file.name)

    longest = max(len(chunk.text) for chunk in chunks)
    print(f"{len(chunks):3} chunks (longest {longest} characters)  {file.name}")

# Show one chunk with all its metadata
print()
print(chunks[0])
