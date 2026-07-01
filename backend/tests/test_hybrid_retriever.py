from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.vector_store import InMemoryVectorStore


def test_hybrid_retriever_combines_lexical_and_dense():
    chunks = [
        {"text": "apple orange banana", "chunk_index": 1},
        {"text": "car bus train", "chunk_index": 2},
    ]
    vs = InMemoryVectorStore()
    vs.add([1.0, 0.0, 0.0], {"chunk_index": 1})
    vs.add([0.0, 1.0, 0.0], {"chunk_index": 2})
    hr = HybridRetriever(chunks, vs)
    res = hr.retrieve("apple", query_vector=[1.0, 0.0, 0.0], top_k=2)
    assert isinstance(res, list)
    assert len(res) >= 1
