"""
Main entry point for reading an uploaded file.

    Uploaded file
         |
    1. Format supported?       no -> "Format not supported" (.docx, .zip, .png ...)
         |                                                    file_checks.py
    2. File has content?       no -> "The file is empty"
         |                                                    file_checks.py
    3. Within size limit?      no -> "File is too large" (over 10 MB)
         |                                                    file_checks.py
    4. File can be read?       no -> PDF:   corrupted, renamed, password-protected, scanned
         |                           TXT:   blank
         |                           CSV:   cannot be read, no data rows
         |                           Excel: corrupted, renamed, all sheets empty
         |                                                    file_extractors.py
         v
    List of Section objects: each has .text and .location (page, sheet or row)

Every failure raises FileReadingError with a message from user_messages.py.
"""
from pathlib import Path

from source_code.document_reading import file_checks
from source_code.document_reading import file_extractors


def validate_and_read_uploaded_file(file_name, file_bytes):
    extension = Path(file_name).suffix.lower()

    # Checks 1-3
    file_checks.check_format_is_supported(extension)
    file_checks.check_file_has_content(file_bytes)
    file_checks.check_size_is_within_limit(file_bytes)

    # Step 4
    if extension == ".pdf":
        return file_extractors.extract_text_from_pdf(file_bytes)
    if extension == ".txt":
        return file_extractors.extract_text_from_txt(file_bytes)
    if extension == ".csv":
        return file_extractors.extract_rows_from_csv(file_bytes)
    if extension == ".xlsx":
        return file_extractors.extract_rows_from_excel(file_bytes)
