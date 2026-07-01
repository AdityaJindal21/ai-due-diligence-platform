from __future__ import annotations

try:
    from sentence_transformers import CrossEncoder
except Exception:
    CrossEncoder = None


class CrossReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.model = None
        if CrossEncoder is not None:
            try:
                self.model = CrossEncoder(model_name)
            except Exception:
                self.model = None

    def rerank(self, query: str, candidates: list, top_k: int = 10):
        """Candidates: list of dict with 'chunk' key containing text."""
        if not self.model:
            # fallback: return candidates as-is with score from candidate
            return candidates[:top_k]
        pairs = [[query, c["chunk"]["text"]] for c in candidates]
        scores = self.model.predict(pairs)
        ranked = list(zip(candidates, scores))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in ranked[:top_k]]
