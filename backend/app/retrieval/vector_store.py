from __future__ import annotations

import math
from typing import List, Tuple


class InMemoryVectorStore:
    def __init__(self):
        self.vectors: List[List[float]] = []
        self.metadatas: List[dict] = []

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        num = 0.0
        suma = 0.0
        sumb = 0.0
        for x, y in zip(a, b):
            num += x * y
            suma += x * x
            sumb += y * y
        if suma == 0 or sumb == 0:
            return 0.0
        return num / (math.sqrt(suma) * math.sqrt(sumb))

    def add(self, vector: List[float], metadata: dict):
        self.vectors.append(vector)
        self.metadatas.append(metadata)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[dict, float]]:
        scores = []
        for meta, vec in zip(self.metadatas, self.vectors):
            score = self._cosine(query_vector, vec)
            scores.append((meta, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
