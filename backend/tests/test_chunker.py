from app.preprocessing.chunker import Chunker
from app.schemas.document import Document, DocumentMetadata, Page
from app.schemas.section import Section


def test_chunk_section_pages_mapping():
    pages = [
        Page(page_number=1, text="A" * 500, character_count=500),
        Page(page_number=2, text="B" * 500, character_count=500),
    ]
    meta = DocumentMetadata(company="Acme", filename="acme.pdf", filing_type="10-K", year=2024, source="SEC", total_pages=2)
    doc = Document(metadata=meta, pages=pages)
    sec = Section(title="ITEM 1", start_page=1, end_page=2, text=pages[0].text + pages[1].text)
    c = Chunker(chunk_size=600, overlap=50)
    chunks, next_idx = c.chunk_section(sec, doc, start_index=1)
    assert len(chunks) >= 2
    assert chunks[0].start_page == 1
    assert chunks[-1].end_page == 2
