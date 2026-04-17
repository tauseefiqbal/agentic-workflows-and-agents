import asyncio
from typing import List, Dict
from anthropic import Anthropic, AsyncAnthropic
from tqdm.asyncio import tqdm_asyncio

class ContextualEmbedder:
    """
    Generate contextual explanations for chunks using Claude
    """
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        
    async def generate_context_for_chunk(
        self, 
        chunk: Dict,
        full_document: str
    ) -> str:
        """
        Generate contextual explanation for a single chunk
        
        This is Anthropic's recommended prompt for contextual retrieval
        """
        
        prompt = f"""<document>
{full_document}
</document>

Here is the chunk we want to situate within the whole document:
<chunk>
{chunk['text']}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else."""

        try:
            # Use prompt caching for the document (same doc, many chunks)
            response = await self.client.beta.prompt_caching.messages.create(
                model=self.model,
                max_tokens=200,  # Context should be concise
                system=[
                    {
                        "type": "text",
                        "text": "You are a helpful assistant that generates concise, informative context for text chunks to improve search retrieval.",
                    },
                    {
                        "type": "text",
                        "text": full_document,
                        "cache_control": {"type": "ephemeral"}  # Cache the document!
                    }
                ],
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            context = response.content[0].text
            return context.strip()
            
        except Exception as e:
            print(f"Error generating context: {e}")
            # Fallback: use metadata as context
            metadata = chunk.get('metadata', {})
            return f"This is from {metadata.get('source', 'unknown source')}."
    
    async def contextualize_chunks(
        self,
        chunks: List[Dict],
        full_document: str,
        max_concurrent: int = 5
    ) -> List[Dict]:
        """
        Generate contexts for all chunks with rate limiting
        
        Args:
            chunks: List of chunk dictionaries
            full_document: Complete document text (will be cached)
            max_concurrent: Max concurrent API calls
            
        Returns:
            List of chunks with added 'context' field
        """
        
        # Create semaphore for rate limiting
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_chunk(chunk):
            async with semaphore:
                context = await self.generate_context_for_chunk(
                    chunk, 
                    full_document
                )
                chunk['context'] = context
                chunk['contextualized_text'] = f"{context}\n\n{chunk['text']}"
                return chunk
        
        # Process all chunks with progress bar
        tasks = [process_chunk(chunk) for chunk in chunks]
        contextualized_chunks = await tqdm_asyncio.gather(
            *tasks,
            desc="Generating contexts"
        )
        
        return contextualized_chunks

# Example usage
async def main():
    contextualizer = ContextualEmbedder(api_key=Config.ANTHROPIC_API_KEY)
    
    # Assuming we have chunks from previous step
    contextualized_chunks = await contextualizer.contextualize_chunks(
        chunks=chunks,
        full_document=document,
        max_concurrent=5  # Respect rate limits
    )
    
    # Check results
    for chunk in contextualized_chunks[:2]:
        print(f"\nOriginal: {chunk['text'][:100]}...")
        print(f"Context: {chunk['context']}")
        print(f"Contextualized: {chunk['contextualized_text'][:200]}...")

# Run async
if __name__ == "__main__":
    asyncio.run(main())

# Without caching: 
# - Full document sent with each chunk
# - 10 chunks × 2000 tokens/document = 20,000 input tokens
# - At $3/M: $0.06 per document

# With caching:
# - First chunk: 2000 tokens written to cache (1.25x = $0.0075)
# - Next 9 chunks: 2000 tokens read from cache (0.1x = $0.0018)
# - Total: $0.009 per document
# - Savings: 85% reduction!