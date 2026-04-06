
# langgraph_guards/state.py

from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    The shared state passed between all nodes in the graph.
    Each guardrail node can read and update this.
    """
    messages: List[BaseMessage]      # full conversation history
    user_input: str                  # the raw user message
    clean_input: str                 # after PII redaction
    blocked: bool                    # was the request blocked?
    block_reason: Optional[str]      # why?
    block_stage: Optional[str]       # where?
    raw_llm_output: Optional[str]    # what the LLM said
    final_output: Optional[str]      # what we'll send to the user
    retry_count: int                 # how many times have we retried?
