import asyncio
import os
from typing import List, Dict
from config import Config
from chunking import DocumentChunker
from contextualizer import ContextualEmbedder
from embeddings import VectorStore
from bm25_index import ContextualBM25
from retriever import HybridRetriever
from reranker import Reranker
from anthropic import Anthropic

class ContextualRAGPipeline:
    """
    Complete Contextual Retrieval RAG pipeline
    """
    
    def __init__(self):
        # Initialize components
        self.chunker = DocumentChunker(
            chunk_size=Config.CHUNK_SIZE,
            overlap=Config.CHUNK_OVERLAP
        )
        
        self.contextualizer = ContextualEmbedder(
            api_key=Config.ANTHROPIC_API_KEY,
            model=Config.CLAUDE_MODEL
        )
        
        self.vector_store = VectorStore(
            voyage_api_key=Config.VOYAGE_API_KEY,
            collection_name=Config.COLLECTION_NAME,
            persist_directory=Config.VECTOR_DB_PATH
        )
        
        self.bm25_index = ContextualBM25()
        
        self.reranker = Reranker(
            cohere_api_key=os.getenv("COHERE_API_KEY")
        )
        
        self.claude = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
    async def index_document(
        self,
        document: str,
        metadata: Dict = None
    ) -> None:
        """
        Index a document with contextual retrieval
        
        Steps:
        1. Chunk document
        2. Generate contexts for chunks
        3. Create embeddings
        4. Build BM25 index
        """
        print("Step 1: Chunking document...")
        chunks = self.chunker.chunk_document(document, metadata)
        print(f"Created {len(chunks)} chunks")
        
        print("\nStep 2: Generating contexts with Claude...")
        contextualized_chunks = await self.contextualizer.contextualize_chunks(
            chunks=chunks,
            full_document=document,
            max_concurrent=5
        )
        
        print("\nStep 3: Creating embeddings and storing...")
        self.vector_store.add_documents(contextualized_chunks)
        
        print("\nStep 4: Building BM25 index...")
        self.bm25_index.build_index(contextualized_chunks)
        
        print("\n✓ Document indexed successfully!")
    
    def query(
        self,
        query: str,
        top_k_retrieval: int = 150,
        top_k_final: int = 20,
        alpha: float = 0.5
    ) -> List[Dict]:
        """
        Query the RAG system
        
        Steps:
        1. Hybrid search (embeddings + BM25)
        2. Rerank results
        3. Return top-k
        """
        print(f"\nQuerying: {query}")
        
        print("\nStep 1: Hybrid search (embeddings + BM25)...")
        retriever = HybridRetriever(
            vector_store=self.vector_store,
            bm25_index=self.bm25_index,
            alpha=alpha
        )
        
        hybrid_results = retriever.hybrid_search(
            query=query,
            top_k=top_k_retrieval
        )
        print(f"Retrieved {len(hybrid_results)} candidates")
        
        print("\nStep 2: Reranking...")
        final_results = self.reranker.rerank(
            query=query,
            documents=hybrid_results,
            top_k=top_k_final
        )
        print(f"Final top-{top_k_final} results")
        
        return final_results
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict]
    ) -> str:
        """
        Generate final answer using Claude with retrieved context
        """
        # Build context from chunks
        context = "\n\n".join([
            f"[Source {i+1}]: {chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Generate answer
        response = self.claude.messages.create(
            model=Config.CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Based on the following context, answer the question. If the answer is not in the context, say so.

Context:
{context}

Question: {query}

Answer:"""
            }]
        )
        
        return response.content[0].text

# Complete usage example
async def main():
    # Initialize pipeline
    pipeline = ContextualRAGPipeline()
    
    # Sample document
    document = """
    ACME Corporation Q2 2023 Earnings Report
    
    Executive Summary:
    ACME Corporation reported strong financial performance in Q2 2023, with revenue reaching $323 million, representing a 3% increase over Q1 2023's $314 million. This growth was primarily driven by increased demand in our enterprise software division.
    
    Revenue Breakdown:
    - Enterprise Software: $180 million (up 5% from Q1)
    - Cloud Services: $95 million (up 2% from Q1)
    - Professional Services: $48 million (flat compared to Q1)
    
    Profitability:
    Gross profit margin improved to 68%, up from 66% in Q1 2023, due to operational efficiencies and improved pricing strategies.
    
    Forward Looking:
    We expect Q3 2023 revenue to be in the range of $330-340 million, representing continued growth momentum.
    """
    
    metadata = {
        "source": "ACME Q2 2023 Earnings Report",
        "date": "2023-07-15",
        "company": "ACME Corporation",
        "type": "financial_report"
    }
    
    # Index document
    print("=" * 60)
    print("INDEXING DOCUMENT")
    print("=" * 60)
    await pipeline.index_document(document, metadata)
    
    # Query the system
    print("\n" + "=" * 60)
    print("QUERYING SYSTEM")
    print("=" * 60)
    
    query = "What was ACME's revenue growth in Q2 2023 and what drove it?"
    
    # Get relevant chunks
    results = pipeline.query(
        query=query,
        top_k_retrieval=50,
        top_k_final=5
    )
    
    # Show results
    print("\n" + "=" * 60)
    print("RETRIEVED CHUNKS")
    print("=" * 60)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Rerank Score: {result['rerank_score']:.3f}")
        print(f"   Text: {result['text'][:200]}...")
    
    # Generate final answer
    print("\n" + "=" * 60)
    print("GENERATING ANSWER")
    print("=" * 60)
    answer = pipeline.generate_answer(query, results[:3])
    print(f"\nAnswer: {answer}")

# Run
if __name__ == "__main__":
    asyncio.run(main())
