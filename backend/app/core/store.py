from __future__ import annotations

from typing import List

from app.schemas.chunk import Chunk
from app.retrieval.vector_store import InMemoryVectorStore
from app.embeddings.embedding_service import EmbeddingService


class InMemoryStore:
    def __init__(self):
        self.chunks: List[Chunk] = []
        self.vector_store = InMemoryVectorStore()
        self.embedder = EmbeddingService()

    def add_chunks(self, chunks: List[Chunk]):
        for c in chunks:
            self.chunks.append(c)
            vec = self.embedder.get_embedding(c.text)
            meta = {"chunk_id": c.chunk_id, "chunk_index": c.chunk_index, "company": c.company, "section": c.section, "start_page": c.start_page, "end_page": c.end_page, "text": c.text}
            self.vector_store.add(vec, meta)
        # also upsert to Chroma if configured
        try:
            if self.embedder.chroma and len(chunks) > 0:
                texts = [c.text for c in chunks]
                metas = [{"chunk_id": c.chunk_id, "company": c.company, "section": c.section, "start_page": c.start_page, "end_page": c.end_page, "chunk_index": c.chunk_index} for c in chunks]
                ids = [c.chunk_id for c in chunks]
                self.embedder.upsert_to_chroma("chunks", texts, metas, ids)
        except Exception:
            pass

    def all_chunks(self) -> List[Chunk]:
        return self.chunks


store = InMemoryStore()
