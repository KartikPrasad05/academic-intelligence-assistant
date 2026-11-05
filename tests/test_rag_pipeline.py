"""
=============================================================================
AUTOMATED INTEGRATION AND REGRESSION TEST SUITE (RAG-17)
Verifies full pipeline integrity, hybrid search, caching, and anti-hallucination.
=============================================================================
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import cfg, DATA_DIR
from document_loader import DocumentLoader
from chunker import DocumentChunker
from vector_store import CloudVectorStore
from retriever import ScalableHybridRetriever
from cache_manager import SemanticCacheManager
from rag_service import ScalableRAGPipeline


@pytest.fixture(scope="module")
def initialized_system():
    loader = DocumentLoader()
    chunker = DocumentChunker(chunk_size=800, overlap=150)
    docs = loader.load_all_documents()
    chunks = chunker.chunk_pages(docs)
    
    vs = CloudVectorStore()
    vs.add_chunks(chunks)
    
    retriever = ScalableHybridRetriever(vs)
    cache = SemanticCacheManager()
    pipeline = ScalableRAGPipeline(retriever=retriever, cache_manager=cache)
    return {
        "loader": loader,
        "chunker": chunker,
        "docs": docs,
        "chunks": chunks,
        "vector_store": vs,
        "retriever": retriever,
        "cache": cache,
        "pipeline": pipeline
    }


def test_document_loader(initialized_system):
    """RAG-6 Acceptance Criteria Verification."""
    docs = initialized_system["docs"]
    assert len(docs) >= 5, f"Expected at least 5 college documents, found {len(docs)}"
    for d in docs:
        assert d.char_count > 100, f"Document {d.doc_name} has insufficient content"
        assert d.page_number >= 1, "Page number must be positive"


def test_text_chunker(initialized_system):
    """RAG-7 Acceptance Criteria Verification."""
    chunks = initialized_system["chunks"]
    assert len(chunks) > 10, "Expected multiple chunks across documents"
    for c in chunks:
        assert len(c.text) <= 1200, "Chunk exceeded maximum threshold"
        assert c.chunk_id is not None, "Chunk ID must be populated"
        assert c.doc_name != "", "Chunk must retain source document name"


def test_vector_search(initialized_system):
    """RAG-9 & RAG-10 Verification."""
    vs = initialized_system["vector_store"]
    results = vs.search("minimum attendance requirement", top_k=3)
    assert len(results) > 0, "Vector search returned zero results"
    top_chunk, score = results[0]
    assert "academic_regulations" in top_chunk["doc_name"].lower()
    assert score > 0.4, f"Cosine similarity score {score} is too low"


def test_hybrid_retriever(initialized_system):
    """RAG-10 Hybrid Retrieval with RRF."""
    retriever = initialized_system["retriever"]
    chunks = retriever.retrieve("What is the fee for attendance condonation?")
    assert len(chunks) > 0
    top = chunks[0]
    assert "academic_regulations" in top.doc_name.lower()
    assert "1,000" in top.text or "condonation" in top.text.lower()


def test_semantic_cache_speedup(initialized_system):
    """Scalability Semantic Cache verification."""
    pipeline = initialized_system["pipeline"]
    query = "What is the detailed procedure for semester examination revaluation?"
    pipeline.cache.clear()
    
    # First call (Cold cache)
    res1 = pipeline.answer_question(query, use_cache=True)
    assert res1.is_cached is False
    
    # Second call (Warm cache hit)
    res2 = pipeline.answer_question(query, use_cache=True)
    assert res2.is_cached is True
    assert res2.latency_ms < 50.0, f"Expected sub-50ms cache response, got {res2.latency_ms}ms"


def test_anti_hallucination_safe_refusal(initialized_system):
    """RAG-14 Verification: Unknown questions must be strictly refused."""
    pipeline = initialized_system["pipeline"]
    unanswerable = "Who will be the chief guest for the next annual sports meet?"
    res = pipeline.answer_question(unanswerable, use_cache=False)
    assert res.is_refusal is True, "System failed to safely refuse an unanswerable question"
    assert cfg.rag.strict_refusal_phrase.lower() in res.answer.lower()
