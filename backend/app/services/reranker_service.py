"""Local reranker service using sentence-transformers CrossEncoder.

Loads a local reranker model from the models/reranker directory.
The model should be a CrossEncoder model (e.g., BAAI/bge-reranker-v2-m3).
"""

import logging
import os
from typing import Any, List

logger = logging.getLogger(__name__)

# Model path: backend/models/reranker/bge-reranker-large/
MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "models",
    "reranker",
    "bge-reranker-large",
)

_reranker = None


def _get_reranker():
    """Lazy-load the reranker CrossEncoder model."""
    global _reranker
    if _reranker is not None:
        return _reranker

    try:
        from sentence_transformers import CrossEncoder
    except ImportError:
        raise ImportError(
            "sentence-transformers not installed. Run:\n"
            "  uv pip install sentence-transformers"
        )

    if not os.path.exists(MODEL_DIR) or not os.listdir(MODEL_DIR):
        logger.warning(f"Reranker model directory is empty: {MODEL_DIR}")
        logger.warning(f"Please place your CrossEncoder model files in: {MODEL_DIR}")
        raise FileNotFoundError(
            f"No reranker model found in {MODEL_DIR}. "
            f"Please copy your model files there."
        )

    logger.info(f"Loading reranker model from: {MODEL_DIR}")
    _reranker = CrossEncoder(MODEL_DIR)
    logger.info("Reranker model loaded successfully")
    return _reranker


def rerank(query: str, documents: List[dict[str, Any]], top_k: int = 5) -> List[dict[str, Any]]:
    """Re-rank documents based on relevance to the query.

    Args:
        query: The user's query string.
        documents: List of documents, each containing at least a 'content' field.
        top_k: Number of top results to return after reranking.

    Returns:
        Re-ranked list of documents with updated 'score' field.
    """
    logger.info(f"Reranking {len(documents)} documents for query")

    if not documents:
        return []

    try:
        reranker = _get_reranker()

        # Prepare pairs: (query, document_content)
        pairs = [(query, doc.get("content", "")) for doc in documents]

        # Get relevance scores
        scores = reranker.predict(pairs).tolist()

        # Attach scores and sort
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = round(float(score), 4)

        ranked = sorted(documents, key=lambda x: x.get("rerank_score", 0), reverse=True)

        logger.info(f"Reranking complete, top score: {ranked[0].get('rerank_score', 0) if ranked else 'N/A'}")
        return ranked[:top_k]

    except Exception as e:
        logger.error(f"Reranking failed, falling back to original order: {e}")
        return documents[:top_k]
