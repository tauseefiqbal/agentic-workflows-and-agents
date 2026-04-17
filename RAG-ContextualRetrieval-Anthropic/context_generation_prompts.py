# Generic prompt (Anthropic's default)
generic_prompt = """Please give a short succinct context to situate 
this chunk within the overall document for the purposes of improving 
search retrieval of the chunk."""

# Domain-specific prompt (legal documents example)
legal_prompt = """Provide context for this legal document chunk. Include:
- Document type (contract, brief, filing, etc.)
- Parties involved
- Relevant dates
- Section or clause reference
- Key legal concepts mentioned
Keep it under 50 words."""

# Use domain-specific prompts for better results