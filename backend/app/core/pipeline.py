from __future__ import annotations

from pathlib import Path
from typing import List

from app.ingestion.loader import load_document
from app.preprocessing.cleaner import TextCleaner
from app.ingestion.section_parser import SectionParser
from app.preprocessing.chunker import Chunker
from app.schemas.chunk import Chunk
from app.core.store import store
from app.db.repository import create_document_record, add_section, add_chunk, init_db


class Pipeline:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.cleaner = TextCleaner()
        self.chunker = Chunker(chunk_size=chunk_size, overlap=overlap)
        try:
            init_db()
        except Exception:
            # DB may not be available in minimal environments
            pass

    def process_pdf(self, pdf_path: Path) -> List[Chunk]:
        doc = load_document(pdf_path)
        doc = self.cleaner.clean_document(doc)
        chunks = self.chunker.chunk_document(doc)
        # index into in-memory store (embeddings + vector store)
        store.add_chunks(chunks)
        # persist metadata and chunks to database when available
        try:
            doc_rec = create_document_record(doc.metadata)
            # sections: use section parser
            parser = SectionParser()
            sections = parser.parse(doc)
            for s in sections:
                add_section(doc_rec.id, s)
            for c in chunks:
                add_chunk(doc_rec.id, c)
        except Exception:
            pass
        return chunks


pipeline = Pipeline()
