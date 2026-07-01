from app.schemas.document import Document, DocumentMetadata, Page
from app.preprocessing.section_parser import SectionParser


def make_doc():
    pages = [
        Page(page_number=1, text="ITEM 1. BUSINESS\nThis is business", character_count=0),
        Page(page_number=2, text="Details about business", character_count=0),
        Page(page_number=3, text="ITEM 1A. RISK FACTORS\nRisks here", character_count=0),
        Page(page_number=4, text="More risks", character_count=0),
    ]
    meta = DocumentMetadata(company="Acme", filename="acme_10k.pdf", filing_type="10-K", year=2024, source="SEC", total_pages=4)
    return Document(metadata=meta, pages=pages)


def test_section_parser_detects_items():
    doc = make_doc()
    p = SectionParser()
    secs = p.parse(doc)
    assert len(secs) == 2
    assert secs[0].start_page == 1
    assert secs[0].end_page == 2
    assert "This is business" in secs[0].text
    assert secs[1].start_page == 3
    assert secs[1].end_page == 4
