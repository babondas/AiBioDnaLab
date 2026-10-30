"""
Automated tests for document reading, written in the same style as C# MSTest / NUnit.

    C# (MSTest)                      Python (unittest)
    [TestClass]                      class ...(unittest.TestCase)
    [TestMethod]                     a method whose name starts with test_
    Assert.IsTrue(x)                 self.assertTrue(x)
    Assert.ThrowsException<T>(...)   with self.assertRaises(T):

Run from the BIODNA folder:
    python -m pytest unit_tests -v
"""
import unittest
from pathlib import Path

from source_code.common import user_messages as messages
from source_code.common.custom_errors import FileReadingError
from source_code.document_reading.document_reader import validate_and_read_uploaded_file

SAMPLES_FOLDER = Path(__file__).resolve().parent.parent / "sample_documents_for_testing"
GOOD_FILES_FOLDER = SAMPLES_FOLDER / "supported_files"
BAD_FILES_FOLDER = SAMPLES_FOLDER / "unsupported_or_broken_files"


def read_sample_file(folder, file_name):
    file_path = folder / file_name
    return validate_and_read_uploaded_file(file_path.name, file_path.read_bytes())


class TestGoodFilesAreRead(unittest.TestCase):

    def check_file_is_read(self, file_name):
        # Act
        sections = read_sample_file(GOOD_FILES_FOLDER, file_name)

        # Assert
        self.assertGreater(len(sections), 0)
        self.assertNotEqual(sections[0].text, "")
        self.assertNotEqual(sections[0].location, "")

    def test_specimen_collection_pdf_is_read(self):
        self.check_file_is_read("BIODNA_SOP_Specimen_Collection_and_Rejection.pdf")

    def test_biomedical_waste_pdf_is_read(self):
        self.check_file_is_read("BIODNA_SOP_Biomedical_Waste_and_Spill_Handling.pdf")

    def test_guidelines_txt_is_read(self):
        self.check_file_is_read("BIODNA_Front_Office_and_Patient_Preparation_Guidelines.txt")

    def test_test_catalog_csv_is_read(self):
        self.check_file_is_read("BIODNA_Test_Catalog.csv")

    def test_reference_ranges_excel_is_read(self):
        self.check_file_is_read("BIODNA_Reference_Ranges_and_Critical_Values.xlsx")

    def test_csv_row_keeps_column_names(self):
        sections = read_sample_file(GOOD_FILES_FOLDER, "BIODNA_Test_Catalog.csv")
        self.assertIn("test_name: Complete Blood Count", sections[0].text)


class TestBadFilesGiveFriendlyErrors(unittest.TestCase):

    def check_file_fails_with_message(self, file_name, expected_message):
        # Act and Assert: reading must raise FileReadingError
        with self.assertRaises(FileReadingError) as error:
            read_sample_file(BAD_FILES_FOLDER, file_name)

        # Assert: the error has the right friendly message
        self.assertIn(expected_message, str(error.exception))

    def test_word_document_is_rejected(self):
        self.check_file_fails_with_message("unsupported_word_document.docx", messages.UNSUPPORTED_MESSAGES[".docx"])

    def test_zip_archive_is_rejected(self):
        self.check_file_fails_with_message("unsupported_archive.zip", messages.UNSUPPORTED_MESSAGES[".zip"])

    def test_image_is_rejected(self):
        self.check_file_fails_with_message("unsupported_image.png", messages.UNSUPPORTED_MESSAGES[".png"])

    def test_empty_file_is_rejected(self):
        self.check_file_fails_with_message("empty_file.txt", messages.FILE_IS_EMPTY)

    def test_blank_txt_is_rejected(self):
        self.check_file_fails_with_message("whitespace_only.txt", messages.TXT_IS_BLANK)

    def test_renamed_pdf_is_rejected(self):
        self.check_file_fails_with_message("renamed_text_file.pdf", messages.PDF_CANNOT_BE_OPENED)

    def test_corrupted_pdf_is_rejected(self):
        self.check_file_fails_with_message("corrupted_document.pdf", messages.PDF_CANNOT_BE_OPENED)

    def test_password_protected_pdf_is_rejected(self):
        self.check_file_fails_with_message("password_protected.pdf", messages.PDF_IS_PASSWORD_PROTECTED)

    def test_scanned_pdf_is_rejected(self):
        self.check_file_fails_with_message("scanned_image_only.pdf", messages.PDF_HAS_NO_TEXT)

    def test_corrupted_excel_is_rejected(self):
        self.check_file_fails_with_message("corrupted_spreadsheet.xlsx", messages.EXCEL_CANNOT_BE_OPENED)

    def test_word_renamed_as_excel_is_rejected(self):
        self.check_file_fails_with_message("word_file_renamed_as_excel.xlsx", messages.EXCEL_CANNOT_BE_OPENED)

    def test_excel_with_empty_sheets_is_rejected(self):
        self.check_file_fails_with_message("empty_sheets.xlsx", messages.EXCEL_SHEETS_ARE_EMPTY)

    def test_csv_with_no_rows_is_rejected(self):
        self.check_file_fails_with_message("csv_header_only.csv", messages.CSV_HAS_NO_ROWS)

    def test_file_over_size_limit_is_rejected(self):
        # Arrange: an 11 MB file created in memory
        too_big = b"x" * (11 * 1024 * 1024)

        # Act and Assert
        with self.assertRaises(FileReadingError) as error:
            validate_and_read_uploaded_file("big_file.txt", too_big)
        self.assertIn(messages.FILE_TOO_LARGE, str(error.exception))