"""Creates the broken and unsupported files used to test BIODNA's error handling.

Run from the BIODNA folder:
    python practice_scripts_for_experiments\create_bad_test_files.py
"""
import os
import zipfile
from pathlib import Path

from openpyxl import Workbook
from PIL import Image, ImageDraw
from pypdf import PdfReader, PdfWriter

PROJECT = Path(__file__).resolve().parent.parent
GOOD = PROJECT / "sample_documents_for_testing" / "supported_files"
BAD = PROJECT / "sample_documents_for_testing" / "unsupported_or_broken_files"
BAD.mkdir(parents=True, exist_ok=True)
good_pdf = GOOD / "BIODNA_SOP_Biomedical_Waste_and_Spill_Handling.pdf"

# Word document, built by hand (a .docx is a zip of XML files)
with zipfile.ZipFile(BAD / "unsupported_word_document.docx", "w") as z:
    z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
    z.writestr("word/document.xml", '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>BIODNA Leave Policy: staff may take 12 casual leaves per year.</w:t></w:r></w:p></w:body></w:document>')

# ZIP archive containing a valid file
with zipfile.ZipFile(BAD / "unsupported_archive.zip", "w") as z:
    z.write(good_pdf, good_pdf.name)

# Image
img = Image.new("RGB", (900, 300), "white")
ImageDraw.Draw(img).text((40, 120), "HbA1c: Lavender top (K2 EDTA)", fill="black")
img.save(BAD / "unsupported_image.png")

# Empty and whitespace-only text files
(BAD / "empty_file.txt").write_bytes(b"")
(BAD / "whitespace_only.txt").write_text("   \n\n\t   \n   ")

# Text file renamed to .pdf
(BAD / "renamed_text_file.pdf").write_text("This is a plain text file renamed to .pdf.")

# Password-protected PDF (password: biodna123)
writer = PdfWriter()
writer.append(PdfReader(good_pdf))
writer.encrypt(user_password="biodna123", owner_password="owner456")
writer.write(BAD / "password_protected.pdf")

# Scanned PDF: an image only, no text
scan = Image.new("RGB", (1240, 1754), "white")
ImageDraw.Draw(scan).text((100, 150), "Scanned copy - Sample Rejection Notice: haemolysed sample", fill="black")
scan.save(BAD / "scanned_image_only.pdf", "PDF", resolution=150)

# Corrupted PDF: a real PDF cut off
data = good_pdf.read_bytes()
(BAD / "corrupted_document.pdf").write_bytes(data[: len(data) // 3])

# Corrupted Excel: correct start, random bytes after
(BAD / "corrupted_spreadsheet.xlsx").write_bytes(b"PK\x03\x04" + os.urandom(2000))

# Word file renamed to .xlsx
(BAD / "word_file_renamed_as_excel.xlsx").write_bytes((BAD / "unsupported_word_document.docx").read_bytes())

# Excel with only empty sheets
wb = Workbook()
wb.active.title = "Haematology"
wb.create_sheet("Biochemistry")
wb.save(BAD / "empty_sheets.xlsx")

# CSV with column names but no rows
(BAD / "csv_header_only.csv").write_text("test_code,test_name,tube_colour,turnaround_time_hours\n")

print(f"Created {len(list(BAD.iterdir()))} files in {BAD}")
