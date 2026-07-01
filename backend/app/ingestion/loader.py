from pathlib import Path
from typing import List

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover - fitz not installed
    fitz = None

from app.schemas.document import Document, DocumentMetadata, Page
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None


def _extract_company_name(filename: str) -> str:
    company = filename.split("_")[0]
    return company.replace("-", " ").title()


def load_document(pdf_path: str | Path) -> Document:
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: list[Page] = []

    if fitz is not None:
        document = fitz.open(pdf_path)
        for page_index, pdf_page in enumerate(document):
            text = pdf_page.get_text("text")
            pages.append(Page(page_number=page_index + 1, text=text, character_count=len(text)))
    elif PdfReader is not None:
        reader = PdfReader(str(pdf_path))
        for page_index, p in enumerate(reader.pages):
            try:
                text = p.extract_text() or ""
            except Exception:
                text = ""
            pages.append(Page(page_number=page_index + 1, text=text, character_count=len(text)))
    else:
        raise RuntimeError("No PDF reader available. Install PyMuPDF or PyPDF2.")

    metadata = DocumentMetadata(
        company=_extract_company_name(pdf_path.stem),
        filename=pdf_path.name,
        filing_type="10-K",
        year=2024,        
        source="SEC EDGAR",
        total_pages=len(pages),
    )

    return Document(
        metadata=metadata,
        pages=pages,
    )