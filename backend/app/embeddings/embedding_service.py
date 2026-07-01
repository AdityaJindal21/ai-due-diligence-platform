from __future__ import annotations

import hashlib
import os
import json
from typing import List, Dict

try:
    import openai
except Exception:
    openai = None

try:
    from app.embeddings.chroma_adapter import ChromaAdapter
except Exception:
    ChromaAdapter = None


class EmbeddingService:
    def __init__(self, provider: str = "openai", model: str = "text-embedding-3-small", cache_dir: str | None = None):
        self.provider = provider
        self.model = model
        self.cache_dir = cache_dir or os.path.join(os.getcwd(), ".emb_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.chroma = None
        if ChromaAdapter is not None and os.environ.get("CHROMA_SERVER"):
            try:
                self.chroma = ChromaAdapter()
            except Exception:
                self.chroma = None

    def _cache_path(self, text: str) -> str:
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{h}.json")

    def get_embedding(self, text: str) -> List[float]:
        path = self._cache_path(text)
        if os.path.exists(path):
            try:
                with open(path, "r") as fh:
                    return json.load(fh)["embedding"]
            except Exception:
                pass

        emb = self._call_provider(text)
        try:
            with open(path, "w") as fh:
                json.dump({"embedding": emb}, fh)
        except Exception:
            pass
        return emb

    def _call_provider(self, text: str) -> List[float]:
        if openai is not None and self.provider == "openai":
            try:
                resp = openai.Embedding.create(input=text, model=self.model)
                return resp["data"][0]["embedding"]
            except Exception:
                pass

        # deterministic fallback: derive 64-d vector from SHA256 digest nibbles
        h = hashlib.sha256(text.encode("utf-8")).hexdigest()
        try:
            raw = bytes.fromhex(h)
        except Exception:
            raw = h.encode("utf-8")

        vec = []
        # convert each byte into two nibbles (high, low) to produce 64 values
        for b in raw:
            high = (b >> 4) & 0x0F
            low = b & 0x0F
            vec.append(high / 15.0)
            vec.append(low / 15.0)

        # normalize
        s = sum(x * x for x in vec) ** 0.5
        if s == 0:
            return vec
        return [x / s for x in vec]

    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        results: List[List[float]] = []
        for t in texts:
            results.append(self.get_embedding(t))
        return results

    def upsert_to_chroma(self, collection: str, texts: List[str], metadatas: List[Dict], ids: List[str]):
        if not self.chroma:
            raise RuntimeError("Chroma not configured")
        vectors = self.batch_embed(texts)
        return self.chroma.upsert(collection, vectors, metadatas, ids)
