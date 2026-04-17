import cohere
from typing import List, Dict

class Reranker:
    """
    Rerank results using a specialized reranking model
    """
    
    def __init__(self, cohere_api_key: str):
        self.cohere_client = cohere.Client(api_key=cohere_api_key)
        self.model = "rerank-english-v3.0"
        
    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 20
    ) -> List[Dict]:
        """
        Rerank documents using Cohere's reranking model
        
        Args:
            query: Search query
            documents: List of document dictionaries with 'text' field
            top_k: Number of top results to return
            
        Returns:
            Reranked documents with relevance scores
        """
        # Extract texts for reranking
        texts = [doc['text'] for doc in documents]
        
        # Rerank
        results = self.cohere_client.rerank(
            model=self.model,
            query=query,
            documents=texts,
            top_n=top_k,
            return_documents=True
        )
        
        # Map results back to original documents
        reranked = []
        for result in results.results:
            original_doc = documents[result.index].copy()
            original_doc['rerank_score'] = result.relevance_score
            original_doc['rerank_index'] = result.index
            reranked.append(original_doc)
        
        return reranked

# Example usage (after hybrid search)
if __name__ == "__main__":
    reranker = Reranker(cohere_api_key=os.getenv("COHERE_API_KEY"))

    # Get top 150 from hybrid search
    hybrid_results = hybrid_retriever.hybrid_search(query, top_k=150)

    # Rerank to get final top 20
    final_results = reranker.rerank(
        query="What was ACME's revenue growth in Q2 2023?",
        documents=hybrid_results,
        top_k=20
    )

    print(f"\nFinal Top 5 (after reranking):")
    for i, result in enumerate(final_results[:5], 1):
        print(f"\n{i}. Rerank Score: {result['rerank_score']:.3f}")
        print(f"   Text: {result['text'][:150]}...")