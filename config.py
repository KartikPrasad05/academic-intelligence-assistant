"""
=============================================================================
COLLEGE DOCUMENT Q&A ASSISTANT (CLOUD RAG WITH CLAUDE INTEGRATION)
Configuration Module - Scalable Cloud-Native Settings
=============================================================================
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"
CACHE_DIR = BASE_DIR / "cache"
TESTS_DIR = BASE_DIR / "tests"

# Ensure directories exist
for directory in [DATA_DIR, CHROMA_DIR, CACHE_DIR, TESTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class CloudLLMConfig:
    """Multi-Platform Claude Configuration."""
    # Active Provider: "anthropic", "aws_bedrock", "gcp_vertex", "openrouter"
    provider: str = os.getenv("LLM_PROVIDER", "anthropic")
    
    # Anthropic Direct API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # AWS Bedrock Claude Integration
    aws_region: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_bedrock_model_id: str = os.getenv(
        "AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    
    # Google Cloud Vertex AI Claude Integration
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "")
    gcp_region: str = os.getenv("GCP_REGION", "us-central1")
    gcp_model_id: str = os.getenv("GCP_MODEL_ID", "claude-3-5-sonnet@20240620")
    
    # Generation Hyperparameters
    temperature: float = 0.0  # Zero temperature for strictly grounded deterministic answers
    max_tokens: int = 1500
    top_p: float = 0.95


@dataclass
class CloudVectorDBConfig:
    """Scalable Cloud Vector Database Configuration."""
    # Active Provider: "chroma_local", "chroma_cloud", "qdrant_cloud", "pinecone"
    provider: str = os.getenv("VECTOR_DB_PROVIDER", "chroma_local")
    
    # Qdrant Cloud Settings
    qdrant_url: str = os.getenv("QDRANT_URL", "https://your-cluster.qdrant.tech:6333")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "college_regulations")
    
    # Pinecone Cloud Settings
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    pinecone_index: str = os.getenv("PINECONE_INDEX", "college-rag-assistant")
    
    # ChromaDB (Local or Remote Cloud Server)
    chroma_persist_dir: str = str(CHROMA_DIR)
    chroma_host: Optional[str] = os.getenv("CHROMA_HOST", None)
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))
    chroma_collection: str = "college_documents"


@dataclass
class CloudEmbeddingConfig:
    """Cloud & Scalable Embeddings Configuration."""
    # Provider: "voyage", "cohere", "bedrock_titan", "openai", "fastembed"
    provider: str = os.getenv("EMBEDDING_PROVIDER", "fastembed")
    
    # Model Names
    voyage_model: str = "voyage-3"
    cohere_model: str = "embed-english-v3.0"
    bedrock_model: str = "amazon.titan-embed-text-v2:0"
    openai_model: str = "text-embedding-3-small"
    fastembed_model: str = "BAAI/bge-small-en-v1.5"
    
    # API Keys
    voyage_api_key: str = os.getenv("VOYAGE_API_KEY", "")
    cohere_api_key: str = os.getenv("COHERE_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    embedding_dimension: int = 384  # Default for BGE-small, 1536 for OpenAI/Voyage


@dataclass
class ScalableRAGConfig:
    """Scalability, Caching, and Retrieval Tuning Parameters."""
    # Document Chunking
    chunk_size: int = 800          # Characters per chunk (optimal for college clauses)
    chunk_overlap: int = 150       # Boundary continuity retention
    
    # Retrieval Configuration
    top_k: int = 4                 # Number of chunks passed to LLM
    similarity_threshold: float = 0.55  # Minimum cosine similarity for valid retrieval
    enable_hybrid_search: bool = True   # Combine Dense Semantic + Sparse BM25
    hybrid_alpha: float = 0.7          # Weight for dense retrieval (1.0 = pure dense, 0.0 = pure BM25)
    enable_reranking: bool = True      # Cross-encoder / contextual reranking
    
    # Scalability: Semantic Cache
    enable_semantic_cache: bool = True
    cache_similarity_threshold: float = 0.92  # Hit cache if query embedding matches >= 92%
    cache_ttl_seconds: int = 86400            # 24-hour cache lifespan
    
    # Strict Anti-Hallucination Guardrail
    strict_refusal_phrase: str = "The requested information was not found in the available documents."
    require_explicit_citation: bool = True


@dataclass
class AppConfig:
    """Master Application Configuration."""
    app_title: str = "Academic Intelligence Assistant"
    app_subtitle: str = "Enterprise Cloud-Native Document Question Answering Assistant"
    college_name: str = "Apex Institute of Science & Technology"
    academic_year: str = "2024-2026"
    
    llm: CloudLLMConfig = field(default_factory=CloudLLMConfig)
    vector_db: CloudVectorDBConfig = field(default_factory=CloudVectorDBConfig)
    embedding: CloudEmbeddingConfig = field(default_factory=CloudEmbeddingConfig)
    rag: ScalableRAGConfig = field(default_factory=ScalableRAGConfig)


# Global Config Singleton
cfg = AppConfig()
