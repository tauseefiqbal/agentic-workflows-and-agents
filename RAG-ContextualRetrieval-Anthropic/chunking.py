import re
from typing import List, Dict
from anthropic import Anthropic

class DocumentChunker:
    """
    Intelligent document chunking that preserves semantic boundaries
    """
    
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk_document(self, document: str, metadata: Dict = None) -> List[Dict]:
        """
        Split document into semantically meaningful chunks
        
        Args:
            document: Full document text
            metadata: Document metadata (title, date, source, etc.)
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Clean document
        document = self._clean_text(document)
        
        # Split by paragraphs first (preserve semantic boundaries)
        paragraphs = self._split_paragraphs(document)
        
        # Create chunks that respect paragraph boundaries
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para.split())
            
            # If single paragraph exceeds chunk size, split it
            if para_length > self.chunk_size:
                # Add current chunk if exists
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Split large paragraph
                sub_chunks = self._split_large_paragraph(para)
                chunks.extend(sub_chunks)
                
            # If adding paragraph would exceed size, start new chunk
            elif current_length + para_length > self.chunk_size:
                chunks.append(" ".join(current_chunk))
                
                # Add overlap from previous chunk
                overlap_words = " ".join(current_chunk).split()[-self.overlap:]
                current_chunk = overlap_words + [para]
                current_length = len(overlap_words) + para_length
                
            # Add paragraph to current chunk
            else:
                current_chunk.append(para)
                current_length += para_length
        
        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        # Format as dictionaries with metadata
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                "text": chunk_text,
                "chunk_id": i,
                "metadata": metadata or {}
            }
            chunk_dicts.append(chunk_dict)
            
        return chunk_dicts
    
    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace and normalize text"""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split on double newlines or paragraph markers
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        return paragraphs
    
    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """Split large paragraph by sentences"""
        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        chunks = []
        current = []
        current_len = 0
        
        for sentence in sentences:
            sent_len = len(sentence.split())
            
            if current_len + sent_len > self.chunk_size:
                if current:
                    chunks.append(" ".join(current))
                current = [sentence]
                current_len = sent_len
            else:
                current.append(sentence)
                current_len += sent_len
        
        if current:
            chunks.append(" ".join(current))
            
        return chunks

# Example usage
if __name__ == "__main__":
    chunker = DocumentChunker(chunk_size=800, overlap=100)

    document = """
ACME Corporation Q2 2023 Earnings Report

Company Overview:
ACME Corporation is a leading provider of enterprise software solutions...

Financial Performance:
Revenue for Q2 2023 reached $323 million, representing a 3% increase 
over Q1 2023's $314 million. This growth was primarily driven by...
"""

    metadata = {
        "source": "ACME Q2 2023 Earnings",
        "date": "2023-07-15",
        "company": "ACME Corporation"
    }

    chunks = chunker.chunk_document(document, metadata)
    print(f"Created {len(chunks)} chunks")