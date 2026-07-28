"""Local embedding service using sentence-transformers.

Loads a local embedding model from the models/embedding directory.
The model files should be a standard sentence-transformers model folder
(e.g., BAAI/bge-small-zh-v1.5, BAAI/bge-base-zh-v1.5, etc.).
"""

import logging
import os
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)

# Model path: backend/models/embedding/
MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "models",
    "embedding",
)

_sentence_transformer = None


def _get_model():
    """Lazy-load the sentence-transformers model."""
    global _sentence_transformer
    if _sentence_transformer is not None:
        return _sentence_transformer

    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise ImportError(
            "sentence-transformers not installed. Run:\n"
            "  uv pip install sentence-transformers"
        )

    if not os.path.exists(MODEL_DIR) or not os.listdir(MODEL_DIR):
        logger.warning(f"Embedding model directory is empty: {MODEL_DIR}")
        logger.warning(f"Please place your sentence-transformers model files in: {MODEL_DIR}")
        raise FileNotFoundError(
            f"No embedding model found in {MODEL_DIR}. "
            f"Please copy your model files there."
        )

    model_name = settings.llm_embedding_model or MODEL_DIR
    logger.info(f"Loading embedding model from: {model_name}")
    _sentence_transformer = SentenceTransformer(model_name)
    logger.info("Embedding model loaded successfully")
    return _sentence_transformer


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts into vector representations.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors.
    """
    logger.info(f"Embedding {len(texts)} texts")

    if not texts:
        return []

    try:
        model = _get_model()
        embeddings = model.encode(texts, show_progress_bar=False).tolist()
        logger.info(f"Successfully embedded {len(embeddings)} texts")
        return embeddings
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise


def embed_query(text: str) -> List[float]:
    """Embed a single query text.

    Args:
        text: Query text to embed.

    Returns:
        Embedding vector.
    """
    logger.info("Embedding query text")

    try:
        model = _get_model()
        embedding = model.encode([text], show_progress_bar=False)[0].tolist()
        return embedding
    except Exception as e:
        logger.error(f"Query embedding failed: {e}")
        raise
