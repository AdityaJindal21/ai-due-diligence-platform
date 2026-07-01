"""Test script for section parsing.

Usage: python scripts/test_sections.py /path/to/apple_10k.pdf

The script will:
- Load the PDF using the loader
- Clean it using TextCleaner
- Parse sections with SectionParser
- Print detected sections and page ranges
"""
import sys
from pathlib import Path

# ensure backend package is importable when running from repo root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.ingestion.loader import extract_pdf_pages
from app.preprocessing.cleaner import TextCleaner
from app.schemas.document import Document, Page, DocumentMetadata
from app.ingestion.section_parser import SectionParser


def build_document_from_pdf(pdf_path: Path, company: str = "Unknown") -> Document:
    pages_text = extract_pdf_pages(pdf_path)
    pages = []
    for i, t in enumerate(pages_text, start=1):
        pages.append(Page(page_number=i, text=t, character_count=len(t)))

    metadata = DocumentMetadata(
        company=company,
        filename=pdf_path.name,
        filing_type="10-K",
        year=0,
        source=str(pdf_path),
        total_pages=len(pages),
    )
    return Document(metadata=metadata, pages=pages)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_sections.py /path/to/10k.pdf")
        return

    pdf = Path(sys.argv[1])
    if not pdf.exists():
        print("PDF not found:", pdf)
        return

    print("Loading PDF...",
          )
    doc = build_document_from_pdf(pdf, company=pdf.stem)

    print("Cleaning document...")
    cleaner = TextCleaner()
    doc = cleaner.clean_document(doc)

    print("Parsing sections...")
    parser = SectionParser()
    sections = parser.parse(doc)

    if not sections:
        print("No sections found.")
        return

    print("Detected sections:")
    for s in sections:
        print(f"- {s.title} -> pages {s.start_page}-{s.end_page}")


if __name__ == '__main__':
    main()
