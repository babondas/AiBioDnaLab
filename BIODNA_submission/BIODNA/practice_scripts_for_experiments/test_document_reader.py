from pathlib import Path

from source_code.document_reading.document_reader import validate_and_read_uploaded_file
from source_code.common.custom_errors import FileReadingError

samples = Path("sample_documents_for_testing")
for folder in [samples / "supported_files", samples / "unsupported_or_broken_files"]:
    print(f"\n=== {folder.name} ===")
    for file in sorted(folder.iterdir()):
        try:
            sections = validate_and_read_uploaded_file(file.name, file.read_bytes())
            print(f"OK     {file.name}  ->  {len(sections)} sections")
        except FileReadingError as error:
            print(f"ERROR  {file.name}  ->  {error}")
