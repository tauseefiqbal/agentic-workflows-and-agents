# Without caching: 
# - Full document sent with each chunk
# - 10 chunks × 2000 tokens/document = 20,000 input tokens
# - At $3/M: $0.06 per document

# With caching:
# - First chunk: 2000 tokens written to cache (1.25x = $0.0075)
# - Next 9 chunks: 2000 tokens read from cache (0.1x = $0.0018)
# - Total: $0.009 per document
# - Savings: 85% reduction!

# Use extended caching for frequently accessed documents
async def contextualize_with_extended_cache(chunks, document):
    response = await client.beta.prompt_caching.messages.create(
        model=Config.CLAUDE_MODEL,
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": document,
                "cache_control": {
                    "type": "ephemeral",
                    "ttl": 3600  # 1 hour cache (costs 2x write, same read)
                }
            }
        ],
        messages=[...]
    )
    
    # Use for documents that will have many chunks processed
    # or will be re-indexed frequently