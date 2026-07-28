"""RAG (Retrieval-Augmented Generation) Service.

Manages the full RAG pipeline:
1. Document chunking and ingestion into Milvus
2. Query embedding and vector search (ANN)
3. Re-ranking with local CrossEncoder model
4. Context formatting for LLM answer generation

Architecture:
  User Query → Embedding → Milvus ANN Search → Reranker → LLM → Answer
                     ↑                          ↑
              Local model (cpu)          Local model (cpu)
"""

import json
import logging
import os
from typing import Any, List

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

from app.core.config import settings
from app.mcp.knowledge_data import get_knowledge_documents
from app.services.embedding_service import embed_query, embed_texts

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────
COLLECTION_NAME = "knowledge_docs"
EMBEDDING_DIM = settings.embedding_dim


def _connect_milvus() -> None:
    """Connect to the Milvus server."""
    connections.connect(
        alias="default",
        host=settings.milvus_host,
        port=settings.milvus_port,
    )


# ═══════════════════════════════════════════════════════════════════
# Collection Management
# ═══════════════════════════════════════════════════════════════════

def _create_collection() -> Collection:
    """Create the knowledge documents collection schema and return it.

    Returns:
        The created (or existing) Collection.
    """
    _connect_milvus()

    # Drop existing collection if re-initializing
    if utility.has_collection(COLLECTION_NAME):
        logger.info(f"Collection '{COLLECTION_NAME}' already exists")
        return Collection(COLLECTION_NAME)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
    ]

    schema = CollectionSchema(fields=fields, description="Knowledge document embeddings")
    collection = Collection(name=COLLECTION_NAME, schema=schema)

    # Create IVF_FLAT index for approximate search
    index_params = {
        "metric_type": "IP",  # Inner product for cosine similarity
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    collection.load()

    logger.info(f"Created collection '{COLLECTION_NAME}' with IVF_FLAT index")
    return collection


# ═══════════════════════════════════════════════════════════════════
# Document Ingestion
# ═══════════════════════════════════════════════════════════════════

def _chunk_document(doc: dict[str, Any]) -> list[dict[str, Any]]:
    """Split a document into smaller chunks for better retrieval.

    Args:
        doc: A knowledge document dictionary.

    Returns:
        List of document chunks.
    """
    content = doc["content"]
    # Split by double newlines (paragraphs), combine small chunks
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = ""
    current_size = 0

    for para in paragraphs:
        para_len = len(para)
        # If adding this paragraph exceeds ~500 chars, save current chunk
        if current_size + para_len > 500 and current_chunk:
            chunks.append({
                "doc_id": doc["id"],
                "title": doc["title"],
                "category": doc["category"],
                "tags": ",".join(doc["tags"]),
                "content": current_chunk.strip(),
            })
            current_chunk = para
            current_size = para_len
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
            current_size += para_len

    # Last chunk
    if current_chunk:
        chunks.append({
            "doc_id": doc["id"],
            "title": doc["title"],
            "category": doc["category"],
            "tags": ",".join(doc["tags"]),
            "content": current_chunk.strip(),
        })

    return chunks


def initialize_knowledge_base() -> dict[str, Any]:
    """Initialize Milvus collection and ingest all knowledge documents.

    This is called once during application startup.

    Returns:
        Summary of ingestion result.
    """
    logger.info("Initializing knowledge base...")

    try:
        collection = _create_collection()

        # Check if already populated
        collection.load()
        existing_count = collection.num_entities
        if existing_count > 0:
            logger.info(f"Knowledge base already has {existing_count} chunks, skipping ingestion")
            return {"status": "skipped", "chunks_count": existing_count}

        # Get and chunk documents
        docs = get_knowledge_documents()
        all_chunks = []
        for doc in docs:
            chunks = _chunk_document(doc)
            all_chunks.extend(chunks)

        logger.info(f"Created {len(all_chunks)} chunks from {len(docs)} documents")

        if not all_chunks:
            return {"status": "empty", "chunks_count": 0}

        # Prepare data for insertion
        doc_ids = [c["doc_id"] for c in all_chunks]
        titles = [c["title"] for c in all_chunks]
        categories = [c["category"] for c in all_chunks]
        tags_list = [c["tags"] for c in all_chunks]
        contents = [c["content"] for c in all_chunks]

        # Generate embeddings
        logger.info("Generating embeddings for all chunks...")
        embeddings = embed_texts(contents)
        logger.info(f"Generated {len(embeddings)} embeddings")

        # Insert into Milvus
        entities = [doc_ids, titles, categories, tags_list, contents, embeddings]
        insert_result = collection.insert(entities)
        collection.flush()

        logger.info(f"Inserted {len(all_chunks)} chunks into Milvus")

        return {
            "status": "success",
            "documents": len(docs),
            "chunks_count": len(all_chunks),
        }

    except Exception as e:
        logger.error(f"Knowledge base initialization failed: {e}")
        return {"status": "error", "error": str(e)}


# ═══════════════════════════════════════════════════════════════════
# Retrieval
# ═══════════════════════════════════════════════════════════════════

def search_knowledge(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search the knowledge base for relevant documents.

    Full RAG pipeline:
    1. Embed the query using local embedding model
    2. Vector search in Milvus (ANN, retrieve more candidates)
    3. Rerank using local CrossEncoder model
    4. Return top-k results

    Args:
        query: User's question text.
        top_k: Number of top results to return after reranking.

    Returns:
        List of relevant document chunks with scores.
    """
    logger.info(f"RAG search: query='{query[:50]}...', top_k={top_k}")

    try:
        _connect_milvus()

        if not utility.has_collection(COLLECTION_NAME):
            logger.warning("Knowledge base not initialized")
            return []

        collection = Collection(COLLECTION_NAME)
        collection.load()

        # Step 1: Embed query using local model
        query_vector = embed_query(query)

        # Step 2: ANN search in Milvus (retrieve more for reranking)
        search_params = {
            "metric_type": "IP",
            "params": {"nprobe": 16},
        }

        # Retrieve 2x top_k for reranker to choose from
        ann_limit = max(top_k * 2, 10)

        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=ann_limit,
            output_fields=["doc_id", "title", "category", "tags", "content"],
        )

        # Format initial results
        initial_results = []
        for hits in results:
            for hit in hits:
                initial_results.append({
                    "doc_id": hit.entity.get("doc_id"),
                    "title": hit.entity.get("title"),
                    "category": hit.entity.get("category"),
                    "tags": hit.entity.get("tags"),
                    "content": hit.entity.get("content"),
                    "score": round(hit.score, 4),
                })

        logger.info(f"ANN search: found {len(initial_results)} candidates")

        if not initial_results:
            return []

        # Step 3: Rerank using local CrossEncoder model
        try:
            from app.services.reranker_service import rerank as rerank_docs
            ranked_results = rerank_docs(query, initial_results, top_k=top_k)
            logger.info(f"Reranking: returned {len(ranked_results)} results")
            return ranked_results
        except (ImportError, FileNotFoundError) as e:
            # Fallback: use ANN order if reranker not available
            logger.warning(f"Reranker unavailable, using ANN order: {e}")
            return initial_results[:top_k]

    except Exception as e:
        logger.error(f"RAG search failed: {e}")
        return []


def format_rag_context(results: list[dict[str, Any]]) -> str:
    """Format search results into a context string for the LLM.

    Args:
        results: Search results from search_knowledge().

    Returns:
        Formatted context string.
    """
    if not results:
        return ""

    sections = []
    for i, r in enumerate(results, 1):
        sections.append(
            f"[参考文档 {i}]\n"
            f"标题: {r['title']}\n"
            f"分类: {r['category']}\n"
            f"相关度: {r['score']}\n"
            f"内容:\n{r['content']}\n"
        )

    return "\n---\n".join(sections)


def drop_and_rebuild_collection(documents: list[dict[str, Any]]) -> dict[str, Any]:
    """Drop existing collection and rebuild with new documents.

    Used for ingesting real PDF documents into the knowledge base.

    Args:
        documents: List of document dicts with id, title, category, tags, content.

    Returns:
        Summary of ingestion result.
    """
    logger.info("Rebuilding knowledge base with new documents...")

    try:
        _connect_milvus()

        # Drop existing collection if it exists
        if utility.has_collection(COLLECTION_NAME):
            utility.drop_collection(COLLECTION_NAME)
            logger.info(f"Dropped existing collection '{COLLECTION_NAME}'")

        # Create fresh collection
        from app.services.rag_service import _create_collection
        # Need to call the module-level function
        _create_collection_internal()

        collection = Collection(COLLECTION_NAME)
        collection.load()

        # Chunk documents
        all_chunks = []
        for doc in documents:
            chunks = _chunk_document(doc)
            all_chunks.extend(chunks)

        logger.info(f"Created {len(all_chunks)} chunks from {len(documents)} documents")

        if not all_chunks:
            return {"status": "empty", "chunks_count": 0}

        # Prepare data for insertion
        doc_ids = [c["doc_id"] for c in all_chunks]
        titles = [c["title"] for c in all_chunks]
        categories = [c["category"] for c in all_chunks]
        tags_list = [c["tags"] for c in all_chunks]
        contents = [c["content"] for c in all_chunks]

        # Generate embeddings
        logger.info("Generating embeddings for all chunks...")
        embeddings = embed_texts(contents)
        logger.info(f"Generated {len(embeddings)} embeddings")

        # Insert into Milvus
        entities = [doc_ids, titles, categories, tags_list, contents, embeddings]
        insert_result = collection.insert(entities)
        collection.flush()

        logger.info(f"Inserted {len(all_chunks)} chunks into Milvus")

        return {
            "status": "success",
            "documents": len(documents),
            "chunks_count": len(all_chunks),
        }

    except Exception as e:
        logger.error(f"Knowledge base rebuild failed: {e}")
        return {"status": "error", "error": str(e)}


def _create_collection_internal():
    """Internal helper to create a fresh Milvus collection."""
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
    ]

    schema = CollectionSchema(fields=fields, description="Knowledge document embeddings")
    collection = Collection(name=COLLECTION_NAME, schema=schema)

    index_params = {
        "metric_type": "IP",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    collection.load()

    logger.info(f"Created collection '{COLLECTION_NAME}' with IVF_FLAT index")
    return collection
