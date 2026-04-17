from rank_bm25 import BM25Okapi
import numpy as np
from typing import List, Dict
import pickle

class ContextualBM25:
    """
    BM25 index using contextualized chunks
    """
    
    def __init__(self):
        self.bm25 = None
        self.chunks = []
        self.tokenized_corpus = []
        
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization - can be improved with nltk/spacy"""
        # Lowercase and split
        tokens = text.lower().split()
        # Remove short tokens
        tokens = [t for t in tokens if len(t) > 2]
        return tokens
    
    def build_index(self, chunks: List[Dict]) -> None:
        """
        Build BM25 index from contextualized chunks
        
        Args:
            chunks: List of chunks with 'contextualized_text' field
        """
        self.chunks = chunks
        
        # Tokenize contextualized text (not just original!)
        self.tokenized_corpus = [
            self._tokenize(chunk['contextualized_text'])
            for chunk in chunks
        ]
        
        # Build BM25 index
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        print(f"Built BM25 index with {len(chunks)} chunks")
    
    def search(self, query: str, top_k: int = 150) -> List[Dict]:
        """
        Search using BM25
        
        Returns chunks with BM25 scores
        """
        # Tokenize query
        tokenized_query = self._tokenize(query)
        
        # Get BM25 scores
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # Return chunks with scores
        results = []
        for idx in top_indices:
            chunk = self.chunks[idx].copy()
            chunk['bm25_score'] = float(scores[idx])
            results.append(chunk)
        
        return results
    
    def save(self, filepath: str) -> None:
        """Save BM25 index to disk"""
        data = {
            'bm25': self.bm25,
            'chunks': self.chunks,
            'tokenized_corpus': self.tokenized_corpus
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, filepath: str) -> None:
        """Load BM25 index from disk"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.bm25 = data['bm25']
        self.chunks = data['chunks']
        self.tokenized_corpus = data['tokenized_corpus']

# Example usage
if __name__ == "__main__":
    bm25_index = ContextualBM25()
    bm25_index.build_index(contextualized_chunks)

    # Search
    results = bm25_index.search(
        query="ACME revenue Q2 2023",
        top_k=20
    )

    print(f"Found {len(results)} matches")
    for result in results[:3]:
        print(f"\nBM25 Score: {result['bm25_score']:.3f}")
        print(f"Text: {result['text'][:100]}...")