"""
=============================================================================
COLLEGE DOCUMENT Q&A ASSISTANT (CLOUD RAG)
Retriever Module (RAG-10: Scalable Hybrid Semantic & BM25 Retriever)
=============================================================================
User Story RAG-10:
As a user,
I want the system to retrieve document sections related to my question
using semantic and keyword signals so that the LLM receives the most
accurate, contextually complete information.

Acceptance Criteria:
1. User question is vectorized and searched against indexed chunks.
2. Hybrid Dense Vector + Sparse BM25 retrieval with Reciprocal Rank Fusion (RRF).
3. Top-k most relevant chunks returned above similarity confidence threshold.
4. Complete source metadata (document, page, section, score) preserved.
=============================================================================
"""

import math
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from config import cfg
from vector_store import CloudVectorStore


@dataclass
class RetrievedChunk:
    """Detailed retrieval item supplied to prompt engineering layer."""
    chunk_id: str
    doc_name: str
    page_number: int
    section: str
    text: str
    score: float
    rank: int
    retrieval_mode: str = "dense"  # "dense", "sparse_bm25", "hybrid_rrf"

    def format_citation(self) -> str:
        """Standardized academic citation format."""
        return f"{self.doc_name} (Page {self.page_number}, Section: {self.section})"


class BM25Retriever:
    """In-memory BM25 sparse keyword retriever for exact term matching."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: Dict[str, int] = {}
        self.avg_doc_len = 0.0
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.corpus: Dict[str, List[str]] = {}
        self.total_docs = 0

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b\w{2,}\b", text)]

    def index(self, chunks: Dict[str, Dict[str, Any]]):
        self.corpus.clear()
        self.doc_len.clear()
        self.doc_freqs.clear()
        self.idf.clear()
        self.total_docs = len(chunks)

        if self.total_docs == 0:
            return

        total_tokens = 0
        for chunk_id, record in chunks.items():
            tokens = self._tokenize(record["text"])
            self.corpus[chunk_id] = tokens
            self.doc_len[chunk_id] = len(tokens)
            total_tokens += len(tokens)

            unique_tokens = set(tokens)
            for t in unique_tokens:
                self.doc_freqs[t] = self.doc_freqs.get(t, 0) + 1

        self.avg_doc_len = (total_tokens / self.total_docs) if self.total_docs > 0 else 1.0

        for t, freq in self.doc_freqs.items():
            self.idf[t] = math.log(1.0 + (self.total_docs - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        query_tokens = self._tokenize(query)
        scores: Dict[str, float] = {}

        for chunk_id, tokens in self.corpus.items():
            doc_len = self.doc_len[chunk_id]
            token_counts: Dict[str, int] = {}
            for t in tokens:
                token_counts[t] = token_counts.get(t, 0) + 1

            score = 0.0
            for qt in query_tokens:
                if qt not in token_counts:
                    continue
                tf = token_counts[qt]
                idf = self.idf.get(qt, 0.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                score += idf * (tf * (self.k1 + 1.0)) / (denom if denom > 0 else 1.0)
            if score > 0:
                scores[chunk_id] = score

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_k]


class ScalableHybridRetriever:
    """
    Scalable Enterprise Retriever combining Dense Semantic Search,
    Sparse BM25 Indexing, and Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, vector_store: Optional[CloudVectorStore] = None):
        self.vector_store = vector_store or CloudVectorStore()
        self.bm25 = BM25Retriever()
        self._refresh_bm25_index()

    def _refresh_bm25_index(self):
        """Refreshes sparse keyword index from vector store chunks."""
        self.bm25.index(self.vector_store.chunks_cache)

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_doc: Optional[str] = None
    ) -> List[RetrievedChunk]:
        """
        Executes hybrid dense-sparse retrieval with score normalization.
        """
        k = top_k or cfg.rag.top_k
        min_threshold = cfg.rag.similarity_threshold

        # Ensure BM25 has latest chunks if database changed
        if len(self.bm25.corpus) != len(self.vector_store.chunks_cache):
            self._refresh_bm25_index()

        # 1. Dense Semantic Search
        dense_results = self.vector_store.search(query, top_k=k * 2, filter_doc=filter_doc)

        if not cfg.rag.enable_hybrid_search or not dense_results:
            # Fall back to pure dense
            chunks = []
            for rank, (record, score) in enumerate(dense_results[:k], start=1):
                if score >= min_threshold:
                    chunks.append(
                        RetrievedChunk(
                            chunk_id=record["chunk_id"],
                            doc_name=record["doc_name"],
                            page_number=record["page_number"],
                            section=record.get("section_title", "General"),
                            text=record["text"],
                            score=round(float(score), 4),
                            rank=rank,
                            retrieval_mode="dense"
                        )
                    )
            return chunks

        # 2. Sparse BM25 Keyword Search
        bm25_results = self.bm25.search(query, top_k=k * 2)

        # 3. Reciprocal Rank Fusion (RRF)
        # RRF_score(d) = sum(1 / (60 + rank_i))
        rrf_scores: Dict[str, float] = {}
        record_map: Dict[str, Dict[str, Any]] = {}
        dense_scores_map: Dict[str, float] = {}

        # Dense ranks
        for rank, (rec, score) in enumerate(dense_results, start=1):
            cid = rec["chunk_id"]
            record_map[cid] = rec
            dense_scores_map[cid] = score
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (cfg.rag.hybrid_alpha * (1.0 / (60.0 + rank)))

        # Sparse BM25 ranks
        filtered_bm25_rank = 1
        for cid, score in bm25_results:
            if cid in self.vector_store.chunks_cache:
                rec = self.vector_store.chunks_cache[cid]
                if filter_doc and rec.get("doc_name") != filter_doc:
                    continue
                record_map[cid] = rec
                rrf_scores[cid] = rrf_scores.get(cid, 0.0) + ((1.0 - cfg.rag.hybrid_alpha) * (1.0 / (60.0 + filtered_bm25_rank)))
                filtered_bm25_rank += 1

        # Sort by combined RRF score
        sorted_rrf = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        final_chunks: List[RetrievedChunk] = []
        for cid, rrf_score in sorted_rrf:
            if len(final_chunks) >= k:
                break
            rec = record_map[cid]
            if filter_doc and rec.get("doc_name") != filter_doc:
                continue
            # Use raw dense cosine score for confidence display, or normalized score
            dense_score = dense_scores_map.get(cid, 0.5)
            
            # Confidence threshold check
            if dense_score >= min_threshold or rrf_score > 0.012:
                final_chunks.append(
                    RetrievedChunk(
                        chunk_id=cid,
                        doc_name=rec["doc_name"],
                        page_number=rec["page_number"],
                        section=rec.get("section_title", "General"),
                        text=rec["text"],
                        score=round(float(dense_score), 4),
                        rank=len(final_chunks) + 1,
                        retrieval_mode="hybrid_rrf"
                    )
                )

        return final_chunks


if __name__ == "__main__":
    from document_loader import DocumentLoader
    from chunker import DocumentChunker
    
    loader = DocumentLoader()
    docs = loader.load_all_documents()
    chunker = DocumentChunker()
    chunks = chunker.chunk_pages(docs)
    
    vs = CloudVectorStore()
    vs.add_chunks(chunks)
    
    retriever = ScalableHybridRetriever(vs)
    res = retriever.retrieve("What is the attendance required to sit for examinations?")
    print(f"Retrieved {len(res)} chunks:")
    for c in res:
        print(f"[{c.rank}] Score: {c.score:.4f} | {c.doc_name} (Page {c.page_number}) - {c.section}")
