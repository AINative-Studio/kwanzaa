"""
Document Processing Service

Handles document text extraction and chunking.
"""

import os
from typing import List, Dict, Any
import PyPDF2
import docx
from sentence_transformers import SentenceTransformer


class DocumentProcessor:
    """Process uploaded documents: extract text, chunk, embed."""

    def __init__(self):
        self.upload_dir = "/tmp/ragbot_uploads"
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = 500  # characters
        self.chunk_overlap = 50

    async def extract_text(self, document_id: str) -> str:
        """Extract text from uploaded document."""
        # Find file
        for filename in os.listdir(self.upload_dir):
            if filename.startswith(document_id):
                filepath = os.path.join(self.upload_dir, filename)

                if filename.endswith('.pdf'):
                    return self._extract_pdf(filepath)
                elif filename.endswith('.txt') or filename.endswith('.md'):
                    return self._extract_text(filepath)
                elif filename.endswith('.docx'):
                    return self._extract_docx(filepath)

        raise FileNotFoundError(f"Document {document_id} not found")

    def _extract_pdf(self, filepath: str) -> str:
        """Extract text from PDF."""
        text = []
        with open(filepath, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            for page in pdf.pages:
                text.append(page.extract_text())
        return '\n'.join(text)

    def _extract_text(self, filepath: str) -> str:
        """Extract text from TXT/MD file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_docx(self, filepath: str) -> str:
        """Extract text from DOCX."""
        doc = docx.Document(filepath)
        return '\n'.join([para.text for para in doc.paragraphs])

    async def generate_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Generate chunks with embeddings."""
        text = await self.extract_text(document_id)

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]

            # Generate embedding
            embedding = self.model.encode(chunk_text).tolist()

            chunks.append({
                "chunk_id": f"{document_id}_chunk_{len(chunks)}",
                "text": chunk_text,
                "chunk_index": len(chunks),
                "embedding_preview": embedding[:10],  # First 10 dims for preview
                "embedding": embedding,  # Full embedding for storage
                "metadata": {
                    "document_id": document_id,
                    "chunk_index": len(chunks),
                    "start_char": start,
                    "end_char": end,
                    "length": len(chunk_text),
                },
            })

            start = end - self.chunk_overlap if end < len(text) else end

        return chunks
