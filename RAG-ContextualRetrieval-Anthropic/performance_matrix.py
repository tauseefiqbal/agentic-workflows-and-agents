from sklearn.metrics import precision_score, recall_score, f1_score
from typing import List, Set, Dict

class RAGEvaluator:
    """
    Evaluate RAG retrieval quality
    """
    
    def evaluate_retrieval(
        self,
        queries: List[str],
        ground_truth: List[Set[str]],  # Relevant chunk IDs per query
        retrieved: List[List[str]]      # Retrieved chunk IDs per query
    ) -> Dict:
        """
        Calculate precision, recall, and F1 for retrieval
        """
        metrics = {
            'precision': [],
            'recall': [],
            'f1': [],
            'mrr': []  # Mean Reciprocal Rank
        }
        
        for i in range(len(queries)):
            truth = ground_truth[i]
            retrieved_ids = retrieved[i]
            
            # Calculate precision@k
            relevant_retrieved = len(set(retrieved_ids) & truth)
            precision = relevant_retrieved / len(retrieved_ids) if retrieved_ids else 0
            
            # Calculate recall@k
            recall = relevant_retrieved / len(truth) if truth else 0
            
            # Calculate F1
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Calculate MRR
            mrr = 0
            for rank, chunk_id in enumerate(retrieved_ids, 1):
                if chunk_id in truth:
                    mrr = 1 / rank
                    break
            
            metrics['precision'].append(precision)
            metrics['recall'].append(recall)
            metrics['f1'].append(f1)
            metrics['mrr'].append(mrr)
        
        # Average metrics
        return {
            'precision@k': np.mean(metrics['precision']),
            'recall@k': np.mean(metrics['recall']),
            'f1@k': np.mean(metrics['f1']),
            'mrr': np.mean(metrics['mrr'])
        }

# Benchmark different approaches (example usage)
# if __name__ == "__main__":
#     evaluator = RAGEvaluator()
#
#     # Compare traditional vs contextual retrieval
#     print("Traditional RAG (no context):")
#     print(evaluator.evaluate_retrieval(queries, ground_truth, traditional_results))
#
#     print("\nContextual Retrieval (embeddings only):")
#     print(evaluator.evaluate_retrieval(queries, ground_truth, contextual_embedding_results))
#
#     print("\nContextual Retrieval (hybrid):")
#     print(evaluator.evaluate_retrieval(queries, ground_truth, hybrid_results))
#
#     print("\nContextual Retrieval (hybrid + reranking):")
#     print(evaluator.evaluate_retrieval(queries, ground_truth, reranked_results))    