"""Test script for the Section-Aware Chunker.

Usage: python3 scripts/test_chunker.py /path/to/10k.pdf

Prints a summary of chunks produced.
"""
import sys
from pathlib import Path

# ensure backend package is importable when running from repo root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app.ingestion.loader import load_document
from app.preprocessing.cleaner import TextCleaner
from app.preprocessing.chunker import Chunker


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/test_chunker.py /path/to/10k.pdf")
        return

    pdf = Path(sys.argv[1])
    if not pdf.exists():
        print("PDF not found:", pdf)
        return

    print("Loading PDF...")
    doc = load_document(pdf)

    print("Cleaning document...")
    cleaner = TextCleaner()
    doc = cleaner.clean_document(doc)

    print("Chunking document by sections...")
    chunker = Chunker(chunk_size=1000, overlap=200)
    chunks = chunker.chunk_document(doc)

    print("=" * 50)
    print("Total Chunks:", len(chunks))
    print("=" * 50)

    for i, c in enumerate(chunks[:10], start=1):
        preview = c.text.replace("\n", " ")[:120]
        print("Chunk", i)
        print("Company:", c.company)
        print("Section:", c.section)
        print("Pages:", f"{c.start_page}-{c.end_page}")
        print("Characters:", c.character_count)
        print("Preview:", preview)
        print("-" * 40)

    if len(chunks) > 10:
        print("... (showing first 10 chunks)")


if __name__ == '__main__':
    main()
