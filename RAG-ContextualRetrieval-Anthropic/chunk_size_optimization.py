# Experiment with different chunk sizes for your domain
if __name__ == "__main__":
    chunk_sizes = [400, 600, 800, 1000]
    best_size = None
    best_performance = 0

    for size in chunk_sizes:
        chunker = DocumentChunker(chunk_size=size)
        # Evaluate retrieval quality
        performance = evaluate_with_chunk_size(size)

        if performance > best_performance:
            best_performance = performance
            best_size = size

    print(f"Optimal chunk size: {best_size}")