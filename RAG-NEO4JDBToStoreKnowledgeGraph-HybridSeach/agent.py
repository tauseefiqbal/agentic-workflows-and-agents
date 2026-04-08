from __future__ import annotations
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
import asyncio
import logging
import os

# Suppress noisy HTTP and Neo4j logs
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('neo4j').setLevel(logging.WARNING)

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import Agent, RunContext
from graphiti_core import Graphiti

from structured_memory import StructuredMemory, MemorySearchResult

load_dotenv()

# ========== Define dependencies ==========
@dataclass
class AgentDependencies:
    """Dependencies for the agent - includes structured memory and optional Graphiti."""
    memory: StructuredMemory
    graphiti_client: Optional[Graphiti] = None

# ========== Helper function to get model configuration ==========
def get_model():
    """Configure and return the LLM model to use."""
    model_choice = os.getenv('MODEL_CHOICE', 'gpt-4.1-mini')
    api_key = os.getenv('OPENAI_API_KEY', 'no-api-key-provided')

    return OpenAIModel(model_choice, provider=OpenAIProvider(api_key=api_key))

# ========== Create the agent ==========
memory_agent = Agent(
    get_model(),
    system_prompt="""You are a helpful assistant with access to a structured memory system.
    Your memory has three tiers:
    1. Short-term: Current conversation facts
    2. Local persistent: Facts saved to disk (always available)
    3. Knowledge graph: Neo4j/Graphiti (available when connected)
    
    Use your search_memory tool to find information. Use remember_fact to store important facts.
    Use memory_status to check which memory tiers are active.
    Answer honestly and indicate which memory tier provided the information when relevant.
    If the knowledge graph is unavailable, rely on local and short-term memory.""",
    deps_type=AgentDependencies
)

# ========== Unified memory search tool ==========
@memory_agent.tool
async def search_memory(ctx: RunContext[AgentDependencies], query: str) -> List[Dict]:
    """Search across all memory tiers (short-term, local, knowledge graph) for relevant facts.
    
    Args:
        ctx: The run context containing dependencies
        query: The search query
        
    Returns:
        A list of memory results with fact, source tier, and relevance
    """
    memory = ctx.deps.memory
    try:
        results = await memory.search(query, limit=10)
        return [
            {
                "fact": r.fact,
                "source": r.source_tier,
                "relevance": round(r.relevance, 3),
                "valid_at": r.valid_at,
                "invalid_at": r.invalid_at,
            }
            for r in results
        ]
    except Exception as e:
        print(f"Error searching memory: {str(e)}")
        return []

# ========== Remember fact tool ==========
@memory_agent.tool
async def remember_fact(ctx: RunContext[AgentDependencies], fact: str, category: str = "general") -> str:
    """Store an important fact in structured memory (short-term + local persistent).
    
    Args:
        ctx: The run context containing dependencies
        fact: The fact to remember
        category: Category of the fact (general, entity, relationship, preference)
        
    Returns:
        Confirmation message
    """
    memory = ctx.deps.memory
    memory.remember(fact=fact, source="agent", category=category, persist=True)
    return f"Remembered: '{fact}' [category={category}]"

# ========== Memory status tool ==========
@memory_agent.tool
async def memory_status(ctx: RunContext[AgentDependencies]) -> Dict[str, str]:
    """Check the status of all memory tiers.
    
    Returns:
        Status of short-term, local, and knowledge graph memory tiers
    """
    return ctx.deps.memory.get_status()

# ========== Main execution function ==========
async def main():
    """Run the agent with structured memory."""
    print("Structured Memory Agent - Three-Tier Memory Architecture")
    print("  Tier 1: Short-term (session)  |  Tier 2: Local (persistent)  |  Tier 3: Knowledge Graph (Neo4j)")
    print("Enter 'exit' to quit. Type '/status' to check memory tiers. Type '/remember <fact>' to store a fact.\n")

    # Neo4j connection parameters
    neo4j_uri = os.environ.get('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.environ.get('NEO4J_USER', 'neo4j')
    neo4j_password = os.environ.get('NEO4J_PASSWORD', 'password')
    
    # Initialize Graphiti client (may or may not connect)
    graphiti_client = Graphiti(neo4j_uri, neo4j_user, neo4j_password)
    
    # Initialize structured memory with all three tiers
    memory = StructuredMemory(
        graphiti_client=graphiti_client,
        storage_path="memory_store.json",
        short_term_limit=100
    )
    
    # Initialize and report tier status
    status = await memory.initialize()
    print("Memory Tier Status:")
    for tier, ok in status.items():
        icon = "[OK]" if ok else "[--]"
        print(f"  {icon} {tier}")
    
    if not status["knowledge_graph"]:
        print("\n  Note: Knowledge graph (Neo4j) is unavailable.")
        print("  The agent will use local persistent memory and short-term memory.")
    print()

    console = Console()
    messages = []
    
    # ========== Run test prompts ==========
    test_prompts = [
        "Which AI assistant is from Anthropic?",
        "What are the key features of GPT-4?",
        "Which is the best LLM currently available?",
    ]

    print("========== Running Test Prompts ==========")
    for prompt in test_prompts:
        try:
            print(f"\n[Test Prompt] {prompt}")
            print("\n[Assistant]")
            with Live('', console=console, vertical_overflow='visible') as live:
                deps = AgentDependencies(memory=memory, graphiti_client=graphiti_client)
                async with memory_agent.run_stream(
                    prompt, deps=deps
                ) as result:
                    curr_message = ""
                    async for message in result.stream_text(delta=True):
                        curr_message += message
                        live.update(Markdown(curr_message))
            # Remember the query context in short-term
            memory.short_term.add(fact=f"User asked: {prompt}", source="user")
            print()
        except Exception as e:
            print(f"\n[Error] Test prompt failed: {str(e)}")
    
    print("\n========== Test Prompts Complete ==========")
    print("You can now ask your own questions.\n")

    try:
        while True:
            try:
                user_input = input("\n[You] ")
            except EOFError:
                break
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("Goodbye!")
                break
            
            # Slash commands
            if user_input.strip() == '/status':
                status = memory.get_status()
                for tier, info in status.items():
                    print(f"  {tier}: {info}")
                continue
            
            if user_input.strip().startswith('/remember '):
                fact = user_input.strip()[10:]
                memory.remember(fact=fact, source="user", persist=True)
                print(f"  Stored: {fact}")
                continue
            
            try:
                # Store the user query in short-term memory
                memory.short_term.add(fact=f"User asked: {user_input}", source="user")
                
                # Build context from memory
                context = memory.get_conversation_context(n=3)
                prompt_with_context = user_input
                if context:
                    prompt_with_context = f"{context}\n\nCurrent question: {user_input}"
                
                print("\n[Assistant]")
                with Live('', console=console, vertical_overflow='visible') as live:
                    deps = AgentDependencies(memory=memory, graphiti_client=graphiti_client)
                    
                    async with memory_agent.run_stream(
                        prompt_with_context, message_history=messages, deps=deps
                    ) as result:
                        curr_message = ""
                        async for message in result.stream_text(delta=True):
                            curr_message += message
                            live.update(Markdown(curr_message))
                    
                    messages.extend(result.all_messages())
                
            except Exception as e:
                print(f"\n[Error] An error occurred: {str(e)}")
    finally:
        await memory.close()
        print("\nMemory system closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        raise
