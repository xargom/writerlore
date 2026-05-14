from typing import Optional
from sentence_transformers import SentenceTransformer

_model: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed(text: str) -> list:
    return _get_model().encode(text).tolist()


def embed_query(text: str) -> list:
    return _get_model().encode(text).tolist()
