from typing import List
import pymupdf


def extract_pdf_contents(pdf_path: str) -> List[str]:
    """
    Extract text contents from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        A list of strings, where each string contains the text content of one page

    Raises:
        FileNotFoundError: If the PDF file does not exist
        PyPDF2.PdfReadError: If the PDF cannot be read
    """
    page_contents: List[str] = []

    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = pymupdf.open(pdf_file)

        for page in pdf_reader.pages():
            text = page.get_text()
            page_contents.append(text)

    return page_contents
