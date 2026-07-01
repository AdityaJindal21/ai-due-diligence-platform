from app.embeddings.embedding_service import EmbeddingService


def test_embedding_fallback_deterministic():
    svc = EmbeddingService(provider="fallback", model="x")
    v1 = svc.get_embedding("hello world")
    v2 = svc.get_embedding("hello world")
    assert v1 == v2
    assert isinstance(v1, list)
    assert len(v1) == 64
