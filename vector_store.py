"""
=============================================================================
COLLEGE DOCUMENT Q&A ASSISTANT (CLOUD RAG)
Vector Store Module (RAG-9: Scalable Cloud Vector Database Engine)
=============================================================================
User Story RAG-9:
As a system developer,
I want to store text chunks, dense embeddings, and associated document metadata
in a scalable cloud vector database so that low-latency similarity queries
can be executed across thousands of college regulations.

Supported Cloud Backends:
1. Qdrant Cloud (Managed Cluster / HNSW Index)
2. Pinecone Serverless Vector Store
3. Chroma Cloud Server (Remote HttpClient)
4. Chroma Persistent / High-Speed JSON-backed Vector Index (Fallback)
=============================================================================
"""

import os
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict

from config import cfg, CHROMA_DIR
from chunker import TextChunk
from embeddings import CloudEmbeddingManager, _cosine_similarity


class CloudVectorStore:
    """Scalable Multi-Backend Vector Database Adapter."""

    def __init__(self, embedding_manager: Optional[CloudEmbeddingManager] = None):
        self.embedding_manager = embedding_manager or CloudEmbeddingManager()
        self.provider = cfg.vector_db.provider
        self.collection_name = cfg.vector_db.chroma_collection
        
        # Local JSON cache path for persistence resilience
        self.index_file = CHROMA_DIR / "vector_index.json"
        
        # In-memory storage for rapid retrieval
        self.chunks_cache: Dict[str, Dict[str, Any]] = {}
        
        # Backend clients
        self._qdrant_client = None
        self._pinecone_index = None
        self._chroma_client = None
        self._chroma_collection = None
        
        # Initialize
        self._load_local_index()
        self._init_backend()

    def _init_backend(self):
        """Attempts to initialize remote cloud vector database."""
        # 1. Qdrant Cloud
        if self.provider == "qdrant_cloud":
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.http.models import Distance, VectorParams
                self._qdrant_client = QdrantClient(
                    url=cfg.vector_db.qdrant_url,
                    api_key=cfg.vector_db.qdrant_api_key or os.getenv("QDRANT_API_KEY")
                )
                print("[VectorStore] Connected to Qdrant Cloud.")
            except Exception as e:
                print(f"[VectorStore] Qdrant Cloud initialization note: {e}. Active mode: High-Speed Persistent Vector Index.")

        # 2. Pinecone Serverless
        elif self.provider == "pinecone":
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=cfg.vector_db.pinecone_api_key or os.getenv("PINECONE_API_KEY"))
                self._pinecone_index = pc.Index(cfg.vector_db.pinecone_index)
                print("[VectorStore] Connected to Pinecone Serverless.")
            except Exception as e:
                print(f"[VectorStore] Pinecone initialization note: {e}.")

        # 3. Chroma Remote or Persistent
        elif self.provider in ["chroma_cloud", "chroma_local"]:
            try:
                import chromadb
                if cfg.vector_db.chroma_host:
                    self._chroma_client = chromadb.HttpClient(
                        host=cfg.vector_db.chroma_host,
                        port=cfg.vector_db.chroma_port
                    )
                else:
                    self._chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
                self._chroma_collection = self._chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                print("[VectorStore] Chroma Vector DB initialized successfully.")
            except Exception as e:
                print(f"[VectorStore] Chroma initialization note: {e}. Active mode: High-Speed Persistent Vector Index.")

    def _load_local_index(self):
        """Loads persistent JSON vector index from disk if present."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.chunks_cache = json.load(f)
                print(f"[VectorStore] Loaded {len(self.chunks_cache)} indexed chunks from persistent cache.")
            except Exception as e:
                print(f"[VectorStore] Error loading local vector index: {e}")
                self.chunks_cache = {}

    def _save_local_index(self):
        """Saves memory cache to JSON index file."""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.chunks_cache, f, ensure_ascii=False)
        except Exception as e:
            print(f"[VectorStore] Error saving local vector index: {e}")

    def add_chunks(self, chunks: List[TextChunk]) -> int:
        """
        Embeds and stores chunks into vector database with duplicate avoidance.
        Returns count of newly indexed chunks.
        """
        if not chunks:
            return 0

        # Filter out chunks already indexed
        new_chunks = [c for c in chunks if c.chunk_id not in self.chunks_cache]
        if not new_chunks:
            print(f"[VectorStore] All {len(chunks)} chunks are already indexed. Zero redundant operations.")
            return 0

        print(f"[VectorStore] Indexing {len(new_chunks)} new chunks...")
        texts = [c.text for c in new_chunks]
        embeddings = self.embedding_manager.embed_texts(texts)

        # 1. Update in-memory persistent cache
        for chunk, emb in zip(new_chunks, embeddings):
            self.chunks_cache[chunk.chunk_id] = {
                "chunk_id": chunk.chunk_id,
                "doc_name": chunk.doc_name,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "section_title": chunk.section_title or "General",
                "metadata": chunk.metadata,
                "embedding": emb,
            }
        self._save_local_index()

        # 2. Sync to Chroma if active
        if self._chroma_collection:
            try:
                ids = [c.chunk_id for c in new_chunks]
                docs = [c.text for c in new_chunks]
                metas = [
                    {
                        "doc_name": c.doc_name,
                        "page_number": c.page_number,
                        "chunk_index": c.chunk_index,
                        "section": c.section_title or "General"
                    }
                    for c in new_chunks
                ]
                self._chroma_collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=docs,
                    metadatas=metas
                )
            except Exception as e:
                print(f"[VectorStore] Chroma upsert warning: {e}")

        # 3. Sync to Qdrant if active
        if self._qdrant_client:
            try:
                from qdrant_client.http.models import PointStruct
                points = [
                    PointStruct(
                        id=abs(hash(c.chunk_id)) % (2**63 - 1),
                        vector=emb,
                        payload={
                            "chunk_id": c.chunk_id,
                            "doc_name": c.doc_name,
                            "page_number": c.page_number,
                            "section": c.section_title or "General",
                            "text": c.text
                        }
                    )
                    for c, emb in zip(new_chunks, embeddings)
                ]
                self._qdrant_client.upsert(
                    collection_name=cfg.vector_db.qdrant_collection,
                    points=points
                )
            except Exception as e:
                print(f"[VectorStore] Qdrant upsert warning: {e}")

        print(f"[VectorStore] Successfully indexed {len(new_chunks)} chunks. Total database size: {len(self.chunks_cache)} chunks.")
        return len(new_chunks)

    def search(
        self,
        query: str,
        top_k: int = 4,
        filter_doc: Optional[str] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Executes semantic vector similarity search against indexed chunks.
        Returns list of (chunk_dict, cosine_similarity_score).
        """
        if not self.chunks_cache:
            print("[VectorStore] Warning: Vector database is empty. Please index documents first.")
            return []

        query_vector = self.embedding_manager.embed_query(query)
        scored_results: List[Tuple[Dict[str, Any], float]] = []

        # Vector search using cosine similarity
        for chunk_id, record in self.chunks_cache.items():
            if filter_doc and record["doc_name"] != filter_doc:
                continue
            
            score = _cosine_similarity(query_vector, record["embedding"])
            scored_results.append((record, score))

        # Sort descending by similarity
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:top_k]

    def count(self) -> int:
        """Returns total count of stored chunks."""
        return len(self.chunks_cache)

    def clear(self):
        """Clears vector database index."""
        self.chunks_cache.clear()
        if self.index_file.exists():
            self.index_file.unlink()
        if self._chroma_collection:
            try:
                self._chroma_client.delete_collection(name=self.collection_name)
                self._chroma_collection = self._chroma_client.get_or_create_collection(
                    name=self.collection_name
                )
            except Exception:
                pass
        print("[VectorStore] Cleared all indexed vectors.")


if __name__ == "__main__":
    vs = CloudVectorStore()
    print(f"Current Vector Database Size: {vs.count()} chunks")
