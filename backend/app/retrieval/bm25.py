from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import List


class BM25:
    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75):
        self.docs = documents
        self.k1 = k1
        self.b = b
        self.N = len(documents)
        self.avgdl = sum(len(self._tokenize(d)) for d in documents) / max(1, self.N)
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self._initialize()

    def _tokenize(self, text: str) -> List[str]:
        return [t for t in text.lower().split() if t]

    def _initialize(self):
        df = defaultdict(int)
        for doc in self.docs:
            tokens = self._tokenize(doc)
            self.doc_len.append(len(tokens))
            freqs = Counter(tokens)
            self.doc_freqs.append(freqs)
            for term in freqs:
                df[term] += 1
        for term, freq in df.items():
            # idf with smoothing
            self.idf[term] = math.log(1 + (self.N - freq + 0.5) / (freq + 0.5))

    def get_scores(self, query: str) -> List[float]:
        qtokens = self._tokenize(query)
        scores = [0.0 for _ in range(self.N)]
        for i in range(self.N):
            doc_len = self.doc_len[i]
            freqs = self.doc_freqs[i]
            score = 0.0
            for term in qtokens:
                if term not in freqs:
                    continue
                idf = self.idf.get(term, 0.0)
                freq = freqs[term]
                denom = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                score += idf * (freq * (self.k1 + 1)) / denom
            scores[i] = score
        return scores

    def get_top_n(self, query: str, n: int = 5):
        scores = self.get_scores(query)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        return ranked[:n]
