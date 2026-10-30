"""Step 4: open a file and extract its text. One function per format.

Each function returns a list of Section objects (see common/data_models.py).
"""
import io
import logging

import pandas as pd
from pypdf import PdfReader

from source_code.common import user_messages as messages
from source_code.common.custom_errors import FileReadingError
from source_code.common.data_models import Section

# Hide pypdf's technical warnings; we show our own friendly messages instead
logging.getLogger("pypdf").setLevel(logging.ERROR)


def extract_text_from_pdf(file_bytes):
    # Open the PDF
    try:
        pdf = PdfReader(io.BytesIO(file_bytes))
    except Exception:
        raise FileReadingError(messages.PDF_CANNOT_BE_OPENED)

    # Stop if it has a password
    if pdf.is_encrypted:
        raise FileReadingError(messages.PDF_IS_PASSWORD_PROTECTED)

    # Read the text of each page
    sections = []
    try:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                sections.append(Section(text=text, location=f"page {page_number}"))
    except Exception:
        raise FileReadingError(messages.PDF_CANNOT_BE_OPENED)

    # Stop if no page had text (a scanned PDF)
    if not sections:
        raise FileReadingError(messages.PDF_HAS_NO_TEXT)
    return sections


def extract_text_from_txt(file_bytes):
    # Read the text (latin-1 is a fallback for files not saved as UTF-8)
    try:
        text = file_bytes.decode("utf-8-sig").strip()
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1").strip()

    # Stop if the file has only spaces or blank lines
    if not text:
        raise FileReadingError(messages.TXT_IS_BLANK)
    return [Section(text=text, location="full text")]


def extract_rows_from_csv(file_bytes):
    # Open the CSV as a table
    try:
        table = pd.read_csv(io.BytesIO(file_bytes))
    except Exception:
        raise FileReadingError(messages.CSV_CANNOT_BE_READ)

    # Turn each row into a section
    sections = convert_table_rows_to_sections(table, location_prefix="")

    # Stop if there were no data rows
    if not sections:
        raise FileReadingError(messages.CSV_HAS_NO_ROWS)
    return sections


def extract_rows_from_excel(file_bytes):
    # Open every sheet in the workbook
    try:
        all_sheets = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
    except Exception:
        raise FileReadingError(messages.EXCEL_CANNOT_BE_OPENED)

    # Turn each row of each sheet into a section
    sections = []
    for sheet_name, table in all_sheets.items():
        sections += convert_table_rows_to_sections(table, location_prefix=f"sheet '{sheet_name}' ")

    # Stop if every sheet was empty
    if not sections:
        raise FileReadingError(messages.EXCEL_SHEETS_ARE_EMPTY)
    return sections


def convert_table_rows_to_sections(table, location_prefix):
    """Turns each row into one line that keeps the column names, for example:
    'test_name: HbA1c | container: Lavender top (K2 EDTA)'"""
    sections = []
    for row_number, row in enumerate(table.to_dict(orient="records"), start=1):
        cells = []
        for column_name, value in row.items():
            if pd.notna(value):                       # skip empty cells
                cells.append(f"{column_name}: {value}")
        if cells:
            sections.append(Section(text=" | ".join(cells), location=f"{location_prefix}row {row_number}"))
    return sections
