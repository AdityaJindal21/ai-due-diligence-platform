from __future__ import annotations

from typing import List, Tuple

try:
    import tiktoken
except Exception:
    tiktoken = None


def split_tokens(text: str, chunk_size: int, overlap: int, encoding_name: str = "cl100k_base") -> List[Tuple[int, int, str]]:
    """Split text by token counts when tiktoken is available. Returns list of (start_char, end_char, substring).

    Falls back to naive character-based splitting if tokenizer not available.
    """
    if not text:
        return []

    if tiktoken is None:
        # fallback to char-based
        results = []
        start = 0
        L = len(text)
        while start < L:
            end = min(start + chunk_size, L)
            results.append((start, end, text[start:end]))
            if end == L:
                break
            start = end - overlap
        return results

    enc = tiktoken.get_encoding(encoding_name)
    toks = enc.encode(text)
    results: List[Tuple[int, int, str]] = []
    start_tok = 0
    L = len(toks)
    while start_tok < L:
        end_tok = min(start_tok + chunk_size, L)
        tok_slice = toks[start_tok:end_tok]
        substring = enc.decode(tok_slice)
        # approximate char offsets by searching substring in text (best-effort)
        idx = text.find(substring)
        if idx == -1:
            # fallback to earlier method
            idx = 0
        results.append((idx, idx + len(substring), substring))
        if end_tok == L:
            break
        start_tok = end_tok - overlap

    return results
