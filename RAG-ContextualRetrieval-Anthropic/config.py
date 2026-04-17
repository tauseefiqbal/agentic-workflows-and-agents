import os
from dotenv import load_dotenv



load_dotenv()
class Config:
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")  # Or use OpenAI/Cohere
    
    # Model Selection
    CLAUDE_MODEL = "claude-sonnet-4-5-20250929"  # For context generation
    EMBEDDING_MODEL = "voyage-2"  # Anthropic recommends Voyage or Gemini
    RERANKER_MODEL = "rerank-2"  # Cohere reranking
    
    # Chunking Parameters
    CHUNK_SIZE = 800  # tokens
    CHUNK_OVERLAP = 100  # tokens
    
    # Retrieval Parameters
    TOP_K_RETRIEVAL = 150  # Initial retrieval
    TOP_K_RERANK = 20      # Final results after reranking
    
    # Caching (for cost optimization)
    USE_PROMPT_CACHING = True
    
    # Vector Database
    VECTOR_DB_PATH = "./chroma_db"
    COLLECTION_NAME = "contextual_rag_collection"