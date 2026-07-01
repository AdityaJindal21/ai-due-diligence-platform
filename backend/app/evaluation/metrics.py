from __future__ import annotations

import time
from typing import List


def precision_at_k(relevant_indices: List[int], retrieved_indices: List[int], k: int) -> float:
    retrieved_k = retrieved_indices[:k]
    num_rel = sum(1 for idx in retrieved_k if idx in relevant_indices)
    return num_rel / k


def mean_reciprocal_rank(relevant_indices: List[int], retrieved_indices: List[int]) -> float:
    for rank, idx in enumerate(retrieved_indices, start=1):
        if idx in relevant_indices:
            return 1.0 / rank
    return 0.0


class Timer:
    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.dt = time.time() - self.t0
*** End Patch