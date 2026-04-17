# Test different weights for embeddings vs BM25
if __name__ == "__main__":
    alphas = [0.3, 0.5, 0.7]
    results = {}

    for alpha in alphas:
        retriever = HybridRetriever(vector_store, bm25_index, alpha=alpha)
        performance = evaluate_retriever(retriever, test_queries)
        results[alpha] = performance

    best_alpha = max(results, key=results.get)
    print(f"Optimal alpha: {best_alpha}")