"""
=============================================================================
COLLEGE DOCUMENT Q&A ASSISTANT (SCALABLE CLOUD RAG)
RAG Service Module (RAG-11 to RAG-14: Pipeline Orchestration & Guardrails)
=============================================================================
User Stories Covered:
- RAG-11: Integrate retrieved context with LLM
- RAG-12: Develop strict grounded RAG prompt
- RAG-13: Implement source citations (Document, Page, Section, Snippet)
- RAG-14: Prevent Hallucination (Strict refusal on unanswerable questions)
- Scalability: Integrated Semantic Cache (<15ms response on recurring queries)
=============================================================================
"""

import time
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

from config import cfg
from retriever import ScalableHybridRetriever, RetrievedChunk
from llm_service import CloudClaudeService, LLMResponse
from cache_manager import SemanticCacheManager


@dataclass
class SourceCitation:
    """Detailed source citation displayed to users."""
    doc_name: str
    page_number: int
    section: str
    chunk_id: str
    similarity_score: float
    snippet: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RAGResult:
    """Complete structured output from the Scalable Cloud RAG Pipeline."""
    question: str
    answer: str
    sources: List[SourceCitation]
    is_cached: bool = False
    cache_similarity: float = 0.0
    latency_ms: float = 0.0
    retrieval_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    model: str = ""
    provider: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    confidence_score: float = 0.0
    is_refusal: bool = False

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["sources"] = [s.to_dict() for s in self.sources]
        return d


class ScalableRAGPipeline:
    """
    Production-grade Scalable RAG Orchestrator with Claude & Semantic Caching.
    """

    SYSTEM_PROMPT = (
        "You are the official academic regulations and college document question-answering assistant.\n"
        "Your mission is to provide accurate, unambiguous answers strictly based on official documents.\n\n"
        "CRITICAL OPERATING RULES:\n"
        "1. Base your answer ONLY on the provided CONTEXT. Do NOT extrapolate or use external general knowledge.\n"
        "2. If the context does NOT contain sufficient factual evidence to answer the question, you MUST reply with EXACTLY:\n"
        f"\"{cfg.rag.strict_refusal_phrase}\"\n"
        "3. Do not invent fees, percentages, names, dates, or guidelines.\n"
        "4. Always mention the source document name and relevant section in your explanation.\n"
        "5. Be concise, professional, and well-structured with bullet points when enumerating rules."
    )

    PROMPT_TEMPLATE = """You are a college information assistant.
Answer the user's question using ONLY the context provided below.
Do not use external knowledge.
If the answer cannot be determined from the context, reply:
"{strict_refusal}"

Give a concise and clear answer.
Mention the source document.

CONTEXT:
{context}

QUESTION:
{question}
"""

    def __init__(
        self,
        retriever: Optional[ScalableHybridRetriever] = None,
        llm_service: Optional[CloudClaudeService] = None,
        cache_manager: Optional[SemanticCacheManager] = None
    ):
        self.retriever = retriever or ScalableHybridRetriever()
        self.llm = llm_service or CloudClaudeService()
        self.cache = cache_manager or SemanticCacheManager()

    def _build_context_string(self, chunks: List[RetrievedChunk]) -> str:
        """Constructs clean numbered context blocks for prompt."""
        if not chunks:
            return "No relevant document sections found in the knowledge base."

        blocks = []
        for i, c in enumerate(chunks, start=1):
            block = (
                f"[DOCUMENT CHUNK {i}]\n"
                f"Source: {c.doc_name}\n"
                f"Page: {c.page_number} | Section: {c.section}\n"
                f"Text:\n{c.text}\n"
            )
            blocks.append(block)
        return "\n".join(blocks)

    def _is_safe_refusal(self, text: str) -> bool:
        """Checks if response correctly triggered anti-hallucination refusal."""
        t = text.lower()
        phrases = [
            "the requested information was not found",
            "information not found in the available documents",
            "not found in the available documents",
            "information was not found",
            "cannot be determined from the context",
            "not mentioned in the provided documents"
        ]
        return any(p in t for p in phrases)

    def answer_question(
        self,
        question: str,
        top_k: Optional[int] = None,
        filter_doc: Optional[str] = None,
        use_cache: bool = True
    ) -> RAGResult:
        """
        Executes end-to-end question answering pipeline:
        1. Check Semantic Cache (Sub-15ms return on hit)
        2. Scalable Hybrid Retrieval (Dense + BM25)
        3. Confidence Threshold & Anti-Hallucination Guardrail
        4. Strict Grounded Prompt Construction
        5. Cloud Claude Answer Synthesis
        6. Citation formatting & Cache Ingestion
        """
        start_total = time.time()
        clean_q = question.strip()

        if not clean_q:
            return RAGResult(
                question=clean_q,
                answer="Please enter a valid question regarding college documents.",
                sources=[],
                latency_ms=0.0
            )

        # -------------------------------------------------------------
        # STEP 1: Scalability Acceleration - Semantic Cache Lookup
        # -------------------------------------------------------------
        if use_cache and cfg.rag.enable_semantic_cache:
            cache_hit = self.cache.lookup(clean_q, filter_doc=filter_doc)
            if cache_hit:
                payload, cache_sim = cache_hit
                total_latency = (time.time() - start_total) * 1000.0
                
                # Reconstruct citations from payload
                citations = [
                    SourceCitation(
                        doc_name=s["doc_name"],
                        page_number=s["page_number"],
                        section=s["section"],
                        chunk_id=s["chunk_id"],
                        similarity_score=s["similarity_score"],
                        snippet=s["snippet"]
                    )
                    for s in payload.get("sources", [])
                ]

                return RAGResult(
                    question=clean_q,
                    answer=payload["answer"],
                    sources=citations,
                    is_cached=True,
                    cache_similarity=round(cache_sim, 4),
                    latency_ms=round(total_latency, 2),
                    retrieval_latency_ms=0.5,
                    llm_latency_ms=0.0,
                    model=payload.get("model", "Semantic-Cache"),
                    provider="Semantic Cache (In-Memory/Redis)",
                    tokens_input=0,
                    tokens_output=0,
                    confidence_score=payload.get("confidence_score", 1.0),
                    is_refusal=payload.get("is_refusal", False)
                )

        # -------------------------------------------------------------
        # STEP 2: Scalable Hybrid Semantic Retrieval
        # -------------------------------------------------------------
        start_retrieval = time.time()
        retrieved_chunks = self.retriever.retrieve(
            query=clean_q,
            top_k=top_k or cfg.rag.top_k,
            filter_doc=filter_doc
        )
        retrieval_ms = (time.time() - start_retrieval) * 1000.0

        # Compute top confidence score
        confidence = retrieved_chunks[0].score if retrieved_chunks else 0.0

        # -------------------------------------------------------------
        # STEP 3: Early Guardrail - If no chunks or confidence too low
        # -------------------------------------------------------------
        if not retrieved_chunks or confidence < cfg.rag.similarity_threshold:
            total_latency = (time.time() - start_total) * 1000.0
            refusal_result = RAGResult(
                question=clean_q,
                answer=cfg.rag.strict_refusal_phrase,
                sources=[],
                is_cached=False,
                latency_ms=round(total_latency, 2),
                retrieval_latency_ms=round(retrieval_ms, 2),
                llm_latency_ms=0.0,
                model="Anti-Hallucination-Guardrail",
                provider="Academic Intelligence Guardrail",
                confidence_score=round(confidence, 4),
                is_refusal=True
            )
            # Store refusal in cache to protect downstream LLM
            if use_cache:
                self.cache.store(clean_q, refusal_result.to_dict(), filter_doc=filter_doc)
            return refusal_result

        # -------------------------------------------------------------
        # STEP 4: Build Grounded Prompt
        # -------------------------------------------------------------
        context_str = self._build_context_string(retrieved_chunks)
        prompt = self.PROMPT_TEMPLATE.format(
            strict_refusal=cfg.rag.strict_refusal_phrase,
            context=context_str,
            question=clean_q
        )

        # -------------------------------------------------------------
        # STEP 5: Send Context to Cloud Claude LLM
        # -------------------------------------------------------------
        start_llm = time.time()
        llm_response = self.llm.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=cfg.llm.temperature,
            max_tokens=cfg.llm.max_tokens
        )
        llm_ms = (time.time() - start_llm) * 1000.0

        # -------------------------------------------------------------
        # STEP 6: Construct Citations & Format Output
        # -------------------------------------------------------------
        citations: List[SourceCitation] = []
        for c in retrieved_chunks:
            # 140 character representative snippet
            snippet = c.text[:160].replace("\n", " ").strip() + "..."
            citations.append(
                SourceCitation(
                    doc_name=c.doc_name,
                    page_number=c.page_number,
                    section=c.section,
                    chunk_id=c.chunk_id,
                    similarity_score=c.score,
                    snippet=snippet
                )
            )

        is_refusal = self._is_safe_refusal(llm_response.content)
        total_latency = (time.time() - start_total) * 1000.0

        final_result = RAGResult(
            question=clean_q,
            answer=llm_response.content.strip(),
            sources=citations if not is_refusal else [],
            is_cached=False,
            latency_ms=round(total_latency, 2),
            retrieval_latency_ms=round(retrieval_ms, 2),
            llm_latency_ms=round(llm_ms, 2),
            model=llm_response.model,
            provider=llm_response.provider,
            tokens_input=llm_response.prompt_tokens,
            tokens_output=llm_response.completion_tokens,
            confidence_score=round(confidence, 4),
            is_refusal=is_refusal
        )

        # Ingest into Semantic Cache for future queries
        if use_cache:
            self.cache.store(clean_q, final_result.to_dict(), filter_doc=filter_doc)

        return final_result


if __name__ == "__main__":
    pipeline = ScalableRAGPipeline()
    q = "What is the minimum attendance required to appear for semester examination?"
    res = pipeline.answer_question(q)
    print("\n--- TEST QUERY 1 ---")
    print(f"Question: {res.question}")
    print(f"Answer:\n{res.answer}")
    print(f"Sources: {[s.doc_name for s in res.sources]}")
    print(f"Latency: {res.latency_ms} ms | Cached: {res.is_cached}")

    # Test cache hit with paraphrased query
    q2 = "How much attendance do I need for semester exams?"
    res2 = pipeline.answer_question(q2)
    print("\n--- TEST QUERY 2 (PARAPHRASED / CACHE CHECK) ---")
    print(f"Question: {res2.question}")
    print(f"Latency: {res2.latency_ms} ms | Cached: {res2.is_cached} | Sim: {res2.cache_similarity}")
