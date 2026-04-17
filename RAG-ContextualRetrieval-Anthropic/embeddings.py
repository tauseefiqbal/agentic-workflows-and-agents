import voyageai
import numpy as np
from typing import List, Dict
import chromadb
from chromadb.config import Settings

class VectorStore:
    """
    Store and retrieve contextual embeddings using ChromaDB
    """
    
    def __init__(
        self,
        voyage_api_key: str,
        collection_name: str = "contextual_rag",
        persist_directory: str = "./chroma_db"
    ):
        # Initialize Voyage AI for embeddings
        # Anthropic recommends Voyage or Gemini embeddings
        self.voyage_client = voyageai.Client(api_key=voyage_api_key)
        self.embedding_model = "voyage-2"
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Cosine similarity
        )
        
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts using Voyage AI
        """
        try:
            result = self.voyage_client.embed(
                texts=texts,
                model=self.embedding_model,
                input_type="document"  # For indexing
            )
            return result.embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
    
    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Add contextualized chunks to vector store
        
        Args:
            chunks: List of chunks with 'contextualized_text' field
        """
        # Extract texts to embed (use contextualized version!)
        texts_to_embed = [chunk['contextualized_text'] for chunk in chunks]
        
        # Generate embeddings in batches
        batch_size = 128
        all_embeddings = []
        
        for i in range(0, len(texts_to_embed), batch_size):
            batch = texts_to_embed[i:i + batch_size]
            embeddings = self.embed_texts(batch)
            all_embeddings.extend(embeddings)
            print(f"Embedded {min(i + batch_size, len(texts_to_embed))}/{len(texts_to_embed)} chunks")
        
        # Prepare data for ChromaDB
        ids = [f"chunk_{chunk['chunk_id']}" for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]  # Original text
        metadatas = [
            {
                **chunk['metadata'],
                'context': chunk['context'],
                'chunk_id': chunk['chunk_id']
            }
            for chunk in chunks
        ]
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=all_embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        print(f"Added {len(chunks)} chunks to vector store")
    
    def similarity_search(
        self,
        query: str,
        top_k: int = 150
    ) -> List[Dict]:
        """
        Perform semantic similarity search
        """
        # Embed query
        query_embedding = self.voyage_client.embed(
            texts=[query],
            model=self.embedding_model,
            input_type="query"  # For search
        ).embeddings[0]
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        chunks = []
        for i in range(len(results['ids'][0])):
            chunk = {
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity
            }
            chunks.append(chunk)
        
        return chunks

# Example usage
if __name__ == "__main__":
    vector_store = VectorStore(
        voyage_api_key=Config.VOYAGE_API_KEY,
        collection_name="acme_earnings"
    )

    # Add contextualized chunks
    vector_store.add_documents(contextualized_chunks)

    # Search
    results = vector_store.similarity_search(
        query="What was ACME's Q2 2023 revenue growth?",
        top_k=20
    )

    print(f"Found {len(results)} similar chunks")
    for result in results[:3]:
        print(f"\nScore: {result['score']:.3f}")
        print(f"Text: {result['text'][:100]}...")