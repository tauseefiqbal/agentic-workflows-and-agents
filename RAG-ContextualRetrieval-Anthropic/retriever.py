from __future__ import annotations
from typing import List, Dict, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from embeddings import VectorStore
    from bm25_index import ContextualBM25

class HybridRetriever:
    """
    Combine semantic search (embeddings) and lexical search (BM25)
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        bm25_index: ContextualBM25,
        alpha: float = 0.5  # Weight for combining scores
    ):
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.alpha = alpha  # 0 = only BM25, 1 = only embeddings
        
    def hybrid_search(
        self,
        query: str,
        top_k: int = 150
    ) -> List[Dict]:
        """
        Perform hybrid search combining embeddings and BM25
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of chunks with combined scores
        """
        # Get results from both methods
        embedding_results = self.vector_store.similarity_search(query, top_k=top_k)
        bm25_results = self.bm25_index.search(query, top_k=top_k)
        
        # Normalize scores to [0, 1] range
        embedding_results = self._normalize_scores(embedding_results, 'score')
        bm25_results = self._normalize_scores(bm25_results, 'bm25_score')
        
        # Combine results
        combined = self._combine_results(
            embedding_results,
            bm25_results,
            self.alpha
        )
        
        # Sort by combined score
        combined = sorted(combined, key=lambda x: x['combined_score'], reverse=True)
        
        return combined[:top_k]
    
    def _normalize_scores(
        self,
        results: List[Dict],
        score_key: str
    ) -> List[Dict]:
        """Normalize scores to [0, 1] range using min-max normalization"""
        if not results:
            return results
            
        scores = [r[score_key] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        
        # Avoid division by zero
        if max_score == min_score:
            for r in results:
                r[f'{score_key}_normalized'] = 1.0
        else:
            for r in results:
                normalized = (r[score_key] - min_score) / (max_score - min_score)
                r[f'{score_key}_normalized'] = normalized
        
        return results
    
    def _combine_results(
        self,
        embedding_results: List[Dict],
        bm25_results: List[Dict],
        alpha: float
    ) -> List[Dict]:
        """
        Combine results using weighted average
        
        Formula: combined_score = alpha * embedding_score + (1-alpha) * bm25_score
        """
        # Create dictionary for quick lookup
        all_chunks = {}
        
        # Add embedding results
        for result in embedding_results:
            chunk_id = result.get('id') or result.get('chunk_id')
            all_chunks[chunk_id] = result
            result['embedding_score_norm'] = result.get('score_normalized', 0)
            result['bm25_score_norm'] = 0  # Will be updated if found in BM25
        
        # Update with BM25 scores
        for result in bm25_results:
            chunk_id = result.get('id') or result.get('chunk_id')
            
            if chunk_id in all_chunks:
                # Chunk found in both methods
                all_chunks[chunk_id]['bm25_score_norm'] = result.get('bm25_score_normalized', 0)
            else:
                # Chunk only in BM25 results
                result['embedding_score_norm'] = 0
                result['bm25_score_norm'] = result.get('bm25_score_normalized', 0)
                all_chunks[chunk_id] = result
        
        # Calculate combined scores
        for chunk in all_chunks.values():
            chunk['combined_score'] = (
                alpha * chunk['embedding_score_norm'] +
                (1 - alpha) * chunk['bm25_score_norm']
            )
        
        return list(all_chunks.values())

# Example usage
if __name__ == "__main__":
    hybrid_retriever = HybridRetriever(
        vector_store=vector_store,
        bm25_index=bm25_index,
        alpha=0.5  # Equal weight to both methods
    )

    results = hybrid_retriever.hybrid_search(
        query="What was ACME's revenue growth in Q2 2023?",
        top_k=150
    )

    print(f"\nTop 5 results:")
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. Combined Score: {result['combined_score']:.3f}")
        print(f"   Embedding: {result['embedding_score_norm']:.3f} | BM25: {result['bm25_score_norm']:.3f}")
        print(f"   Text: {result['text'][:150]}...")