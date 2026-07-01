"""Ingest the sample PDF and index into the in-memory store."""
from pathlib import Path
from app.core.pipeline import pipeline


def main():
    pdf = Path("data/raw/apple_10k.pdf")
    if not pdf.exists():
        print("PDF not found at", pdf)
        return
    print("Processing and indexing... this may take a moment")
    chunks = pipeline.process_pdf(pdf)
    print("Indexed chunks:", len(chunks))


if __name__ == '__main__':
    main()
