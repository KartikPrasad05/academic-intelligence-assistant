"""
=============================================================================
COLLEGE DOCUMENT Q&A ASSISTANT (CLOUD RAG)
Document Loader Module (RAG-6: PDF Text Extractor)
=============================================================================
User Story RAG-6:
As a system developer,
I want to extract text from uploaded PDF and text documents
so that their contents can be processed by the RAG system.

Acceptance Criteria:
1. System accepts PDF documents and text files.
2. Text is extracted from all readable pages with page numbers.
3. File name and document metadata are retained.
4. Empty pages or malformed streams do not cause application failure.
=============================================================================
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# Silence low-level PDF parsing warnings
logging.getLogger("pypdf").setLevel(logging.ERROR)


@dataclass
class DocumentPage:
    """Represents text extracted from a single page or document segment."""
    doc_name: str
    page_number: int
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    char_count: int = 0
    
    def __post_init__(self):
        self.char_count = len(self.text)


class DocumentLoader:
    """Enterprise-grade document loader for PDF, TXT, and Markdown files."""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).resolve().parent / "data"

    def extract_from_pdf(self, file_path: Path) -> List[DocumentPage]:
        """
        Extracts text from PDF file page by page using PyPDF with fallback.
        Gracefully handles empty pages and formatting anomalies.
        """
        pages: List[DocumentPage] = []
        doc_name = file_path.name
        
        # Method 1: Try PyPDF
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            total_pages = len(reader.pages)
            
            for page_idx, page in enumerate(reader.pages):
                page_no = page_idx + 1
                try:
                    page_text = page.extract_text() or ""
                except Exception:
                    page_text = ""
                
                # Clean up whitespace
                cleaned_text = " ".join(page_text.split())
                if cleaned_text:
                    pages.append(
                        DocumentPage(
                            doc_name=doc_name,
                            page_number=page_no,
                            text=cleaned_text,
                            metadata={
                                "source": doc_name,
                                "page": page_no,
                                "total_pages": total_pages,
                                "file_path": str(file_path),
                                "format": "pdf",
                            }
                        )
                    )
            if pages:
                total_extracted_chars = sum(len(p.text) for p in pages)
                companion_txt = file_path.with_suffix(".txt")
                if total_extracted_chars < 800 and companion_txt.exists():
                    return self.extract_from_text(companion_txt, source_name=doc_name)
                return pages
        except ImportError:
            pass
        except Exception as e:
            print(f"[DocumentLoader] PyPDF reading warning for {doc_name}: {e}")

        # Method 2: Fallback to companion text file if available
        companion_txt = file_path.with_suffix(".txt")
        if companion_txt.exists():
            return self.extract_from_text(companion_txt, source_name=doc_name)
            
        return pages

    def extract_from_text(self, file_path: Path, source_name: Optional[str] = None) -> List[DocumentPage]:
        """Extracts text from plain text or markdown files."""
        doc_name = source_name or file_path.name
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            print(f"[DocumentLoader] Error reading {file_path}: {e}")
            return []

        # Split into logical pages if large, or treat as Page 1
        return [
            DocumentPage(
                doc_name=doc_name,
                page_number=1,
                text=content.strip(),
                metadata={
                    "source": doc_name,
                    "page": 1,
                    "total_pages": 1,
                    "file_path": str(file_path),
                    "format": "text",
                }
            )
        ]

    def load_document(self, file_path: Path) -> List[DocumentPage]:
        """Loads a single document based on extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            # If PDF extraction yields nothing or PDF is not yet compiled, check txt companion
            pages = self.extract_from_pdf(file_path)
            if not pages:
                comp = file_path.with_suffix(".txt")
                if comp.exists():
                    pages = self.extract_from_text(comp, source_name=file_path.name)
            return pages
        elif suffix in [".txt", ".md", ".json"]:
            return self.extract_from_text(file_path)
        else:
            print(f"[DocumentLoader] Unsupported file format: {suffix}")
            return []

    def load_all_documents(self) -> List[DocumentPage]:
        """Loads all documents from the data directory."""
        all_pages: List[DocumentPage] = []
        if not self.data_dir.exists():
            return all_pages

        seen_basenames = set()
        
        # Priority: Look for PDF files first
        pdf_files = list(self.data_dir.glob("*.pdf"))
        for p in pdf_files:
            pages = self.load_document(p)
            if pages:
                all_pages.extend(pages)
                seen_basenames.add(p.stem)

        # Then look for .txt files that do NOT have a processed PDF
        txt_files = list(self.data_dir.glob("*.txt"))
        for t in txt_files:
            # Map foo.txt to foo.pdf as source if desired
            canonical_source = f"{t.stem}.pdf"
            if t.stem not in seen_basenames:
                pages = self.extract_from_text(t, source_name=canonical_source)
                all_pages.extend(pages)
                seen_basenames.add(t.stem)

        print(f"[DocumentLoader] Successfully loaded {len(all_pages)} document sections from {len(seen_basenames)} documents.")
        return all_pages


if __name__ == "__main__":
    loader = DocumentLoader()
    docs = loader.load_all_documents()
    print(f"Loaded {len(docs)} documents.")
    for d in docs:
        print(f" - {d.doc_name} (Page {d.page_number}): {d.char_count} chars")
