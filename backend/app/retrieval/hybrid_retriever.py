from __future__ import annotations

from typing import List, Tuple

from app.retrieval.bm25 import BM25
from app.retrieval.vector_store import InMemoryVectorStore


class HybridRetriever:
    def __init__(self, chunks: List[dict], vector_store: InMemoryVectorStore):
        # chunks: list of metadata dicts with 'text'
        self.chunks = chunks
        texts = [c.get("text", "") for c in chunks]
        self.bm25 = BM25(texts)
        self.vs = vector_store

    def retrieve(self, query: str, query_vector: List[float] | None = None, top_k: int = 10):
        bm25_scores = self.bm25.get_scores(query)
        bm25_ranked = sorted(enumerate(bm25_scores), key=lambda x: x[1], reverse=True)

        bm25_top = {i: score for i, score in bm25_ranked[: top_k * 2]}

        vs_results = []
        if query_vector is not None:
            vs_results = self.vs.search(query_vector, top_k=top_k * 2)

        # combine: take union of candidates
        candidates = set(bm25_top.keys())
        for meta, _ in vs_results:
            idx = meta.get("chunk_index") - 1
            candidates.add(idx)

        scored = []
        for idx in candidates:
            bm = bm25_top.get(idx, 0.0)
            vs_score = 0.0
            if query_vector is not None:
                # find meta
                for m, s in vs_results:
                    if (m.get("chunk_index") - 1) == idx:
                        vs_score = s
                        break
            # simple weighted sum
            score = 0.6 * bm + 0.4 * vs_score
            scored.append((idx, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, score in scored[:top_k]:
            c = self.chunks[idx]
            results.append({"chunk": c, "score": score})
        return results
