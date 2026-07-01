from __future__ import annotations

import os
import requests
from typing import List, Dict

CHROMA_SERVER = os.environ.get("CHROMA_SERVER")


class ChromaAdapter:
    def __init__(self, server_url: str | None = None):
        self.server = server_url or CHROMA_SERVER
        if not self.server:
            raise RuntimeError("CHROMA_SERVER not configured")
        self.base = self.server.rstrip("/") + "/api"

    def upsert(self, collection: str, vectors: List[List[float]], metadatas: List[Dict], ids: List[str]):
        url = f"{self.base}/collections/{collection}/add"
        payload = {"ids": ids, "metadatas": metadatas, "embeddings": vectors}
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    def query(self, collection: str, query_vector: List[float], top_k: int = 10):
        url = f"{self.base}/collections/{collection}/query"
        payload = {"query_embeddings": [query_vector], "n_results": top_k}
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        # expected format depends on server version; normalize
        results = data.get("results") or data.get("data")
        return results
