"""RAG step 1: clean the text read from a document.

Removes from every page:
    - extra spaces
    - blank lines
    - headers and footers (lines that appear on every page)
    - page numbers like "Page 3"

Usage:
    cleaner = DataCleaner()
    clean_sections = cleaner.clean_sections(sections)
"""
from source_code.common.data_models import Section


class DataCleaner:

    def clean_sections(self, sections: list[Section]) -> list[Section]:
        """Main method: cleans every page and returns the cleaned pages."""
        header_lines = self.find_header_lines(sections)

        cleaned_sections = []
        for section in sections:
            good_lines = []
            for line in self.get_lines(section.text):
                if self.is_useful_line(line, header_lines):
                    good_lines.append(line)

            if len(good_lines) > 0:
                cleaned_text = "\n".join(good_lines)
                cleaned_sections.append(Section(text=cleaned_text, location=section.location))

        return cleaned_sections

    def get_lines(self, text: str) -> list[str]:
        """Splits text into lines and removes extra spaces from each line."""
        lines = []
        for line in text.split("\n"):
            lines.append(" ".join(line.split()))     # "  a   b  " becomes "a b"
        return lines

    def is_useful_line(self, line: str, header_lines: list[str]) -> bool:
        """A line is useful if it is not blank, not a header, and not a page number."""
        if line == "":
            return False
        if line in header_lines:
            return False
        if self.is_page_number(line):
            return False
        return True

    def is_page_number(self, line: str) -> bool:
        """True for lines like 'Page 3'."""
        return line.startswith("Page ") and line[5:].isdigit()

    def find_header_lines(self, sections: list[Section]) -> list[str]:
        """A header or footer is a line that appears on every page."""
        if len(sections) < 2:
            return []                                # one page: nothing repeats

        header_lines = []
        for line in self.get_lines(sections[0].text):
            if len(line) < 4:
                continue                             # ignore short lines like "1" or "5"
            if self.appears_on_every_page(line, sections):
                header_lines.append(line)
        return header_lines

    def appears_on_every_page(self, line: str, sections: list[Section]) -> bool:
        for section in sections:
            if line not in self.get_lines(section.text):
                return False
        return True
