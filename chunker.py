"""
=============================================================================
COLLEGE DOCUMENT Q&A ASSISTANT (CLOUD RAG)
Chunker Module (RAG-7: Text Chunking & Semantic Boundary Preservation)
=============================================================================
User Story RAG-7:
As a system developer,
I want to divide extracted document text into semantically cohesive chunks
with configurable overlap so that information near boundaries is preserved
and retrieval precision is maximized.

Acceptance Criteria:
1. Documents are divided into chunks respecting size and overlap parameters.
2. Chunk boundaries respect paragraphs and sentences where possible.
3. Every chunk retains rich metadata (doc_name, page, chunk_index, section).
4. Content hashing ensures zero duplicate chunk storage.
=============================================================================
"""

import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from document_loader import DocumentPage


@dataclass
class TextChunk:
    """Represents a coherent text snippet indexed in the vector database."""
    chunk_id: str
    doc_name: str
    page_number: int
    chunk_index: int
    text: str
    char_length: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    section_title: Optional[str] = None


class DocumentChunker:
    """
    Scalable recursive text chunker with paragraph and sentence boundary awareness.
    """

    def __init__(self, chunk_size: int = 800, overlap: int = 150):
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Separators in order of preference
        self.separators = ["\n\nSection", "\n\n", "\n", ". ", "; ", ", ", " "]

    def _generate_chunk_id(self, doc_name: str, page_no: int, chunk_idx: int, text: str) -> str:
        """Deterministic chunk hash for deduplication and indexing."""
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", Path(doc_name).stem)
        return f"{clean_name}_p{page_no}_c{chunk_idx}_{content_hash}"

    def _extract_active_section(self, text: str) -> Optional[str]:
        """Detects section headings within text to enrich chunk metadata."""
        match = re.search(r"(?:Section\s+\d+[:\w\s]+|^\d+\.\d+\s+[A-Z][^\n]+)", text, re.MULTILINE)
        if match:
            return match.group(0).strip()
        return None

    def chunk_text(self, text: str, doc_name: str, page_number: int = 1) -> List[TextChunk]:
        """
        Splits single document text into overlapping chunks respecting natural boundaries.
        """
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        total_len = len(clean_text)
        
        # If text is smaller than chunk size, return single chunk
        if total_len <= self.chunk_size:
            section = self._extract_active_section(clean_text)
            chunk_id = self._generate_chunk_id(doc_name, page_number, 0, clean_text)
            return [
                TextChunk(
                    chunk_id=chunk_id,
                    doc_name=doc_name,
                    page_number=page_number,
                    chunk_index=0,
                    text=clean_text,
                    char_length=total_len,
                    section_title=section,
                    metadata={
                        "source": doc_name,
                        "page": page_number,
                        "chunk_index": 0,
                        "section": section or "General",
                    }
                )
            ]

        chunks: List[TextChunk] = []
        start = 0
        chunk_idx = 0
        current_section = "General Overview"

        while start < total_len:
            end = min(start + self.chunk_size, total_len)
            
            # If not at the end of text, find the best natural breakpoint
            if end < total_len:
                best_break = -1
                window = clean_text[start:end]
                
                # Check for paragraph break
                para_pos = window.rfind("\n\n")
                if para_pos > int(self.chunk_size * 0.5):
                    best_break = start + para_pos
                else:
                    # Check for sentence end
                    sentence_pos = max(window.rfind(". "), window.rfind(".\n"))
                    if sentence_pos > int(self.chunk_size * 0.4):
                        best_break = start + sentence_pos + 1
                    else:
                        # Check for newline or space
                        space_pos = window.rfind(" ")
                        if space_pos > int(self.chunk_size * 0.3):
                            best_break = start + space_pos
                
                if best_break != -1 and best_break > start:
                    end = best_break

            chunk_content = clean_text[start:end].strip()
            
            if chunk_content:
                # Track latest section title
                detected_section = self._extract_active_section(chunk_content)
                if detected_section:
                    current_section = detected_section

                chunk_id = self._generate_chunk_id(doc_name, page_number, chunk_idx, chunk_content)
                chunks.append(
                    TextChunk(
                        chunk_id=chunk_id,
                        doc_name=doc_name,
                        page_number=page_number,
                        chunk_index=chunk_idx,
                        text=chunk_content,
                        char_length=len(chunk_content),
                        section_title=current_section,
                        metadata={
                            "source": doc_name,
                            "page": page_number,
                            "chunk_index": chunk_idx,
                            "section": current_section,
                        }
                    )
                )
                chunk_idx += 1

            # Advance start by (chunk_size - overlap)
            step = max(end - start - self.overlap, 100)
            start += step

        return chunks

    def chunk_pages(self, pages: List[DocumentPage]) -> List[TextChunk]:
        """Processes a list of extracted document pages into vector-ready chunks."""
        all_chunks: List[TextChunk] = []
        for page in pages:
            chunks = self.chunk_text(
                text=page.text,
                doc_name=page.doc_name,
                page_number=page.page_number
            )
            all_chunks.extend(chunks)
        print(f"[DocumentChunker] Chunked {len(pages)} pages into {len(all_chunks)} semantically bounded chunks.")
        return all_chunks


if __name__ == "__main__":
    from document_loader import DocumentLoader
    loader = DocumentLoader()
    docs = loader.load_all_documents()
    chunker = DocumentChunker(chunk_size=800, overlap=150)
    chunks = chunker.chunk_pages(docs)
    print(f"Total Chunks: {len(chunks)}")
    if chunks:
        print(f"Sample Chunk 0:\nID: {chunks[0].chunk_id}\nSource: {chunks[0].doc_name}\nSection: {chunks[0].section_title}\nText: {chunks[0].text[:120]}...\n")
