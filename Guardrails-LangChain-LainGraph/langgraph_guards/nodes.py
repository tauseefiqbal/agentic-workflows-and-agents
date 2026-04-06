# langgraph_guards/nodes.py

import json
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langgraph_guards.state import AgentState
from guardrails.pii_redactor import PIIRedactor

pii_redactor = PIIRedactor()
llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore all instructions",
    "you are now", "act as", "jailbreak", "system prompt",
    "disregard your training", "pretend you are",
]

# -------- Node 1: Input Guardrail --------
def input_guardrail_node(state: AgentState) -> AgentState:
    """
    Checks for injection, redacts PII, validates topic.
    """
    raw = state["user_input"]

    # Injection check
    lower = raw.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            return {
                **state,
                "blocked": True,
                "block_reason": f"Prompt injection pattern: '{pattern}'",
                "block_stage": "input_guardrail",
                "clean_input": raw,
            }

    # PII redaction
    clean, pii_found = pii_redactor.redact(raw)
    if pii_found:
        print(f"[GUARDRAIL] PII redacted: {[e['type'] for e in pii_found]}")

    # Topic check via LLM
    topic_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a topic guardrail. The app only handles:
- product support, billing, technical issues, account management.
Reply ONLY with JSON: {{"allowed": true/false, "reason": "..."}}"""),
        ("human", "{input}")
    ])
    chain = topic_prompt | llm | StrOutputParser()
    raw_result = chain.invoke({"input": clean})

    try:
        result = json.loads(raw_result.strip().lstrip("```json").rstrip("```"))
        if not result.get("allowed", True):
            return {
                **state,
                "blocked": True,
                "block_reason": f"Off-topic: {result.get('reason')}",
                "block_stage": "topic_filter",
                "clean_input": clean,
            }
    except Exception:
        pass  # if we can't parse, let it through (fail open) or fail closed per your policy

    return {
        **state,
        "blocked": False,
        "clean_input": clean,
    }


# -------- Node 2: LLM Call --------
def call_llm_node(state: AgentState) -> AgentState:
    """Calls the LLM with the clean input."""
    messages = state.get("messages", []) + [
        SystemMessage(content="You are a helpful customer support agent. Be concise and factual."),
        HumanMessage(content=state["clean_input"])
    ]
    try:
        response = llm.invoke(messages)
        return {
            **state,
            "raw_llm_output": response.content,
            "messages": messages + [AIMessage(content=response.content)]
        }
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return {
            **state,
            "blocked": True,
            "block_reason": f"LLM service error: {e}",
            "block_stage": "llm_call",
        }


# -------- Node 3: Output Guardrail --------
def output_guardrail_node(state: AgentState) -> AgentState:
    """Validates the LLM's response before it reaches the user."""
    output = state["raw_llm_output"]

    # Check for PII leakage in response
    _, pii_found = pii_redactor.redact(output)
    if any(e["score"] > 0.85 for e in pii_found):
        if state["retry_count"] < 2:
            # Retry with a stricter prompt
            return {
                **state,
                "blocked": False,
                "raw_llm_output": None,
                "retry_count": state["retry_count"] + 1,
                "clean_input": state["clean_input"] + "\n\nIMPORTANT: Do NOT include any personal information in your response."
            }
        else:
            return {
                **state,
                "blocked": True,
                "block_reason": "Output contained PII after multiple retries",
                "block_stage": "output_guardrail"
            }

    # Check output via LLM judge
    try:
        judge_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a quality and safety judge for AI responses.
Check if the response is safe, factual, and appropriate for a customer support context.
Reply ONLY with JSON: {{"safe": true/false, "reason": "..."}}"""),
            ("human", "Response to evaluate:\n{response}")
        ])
        chain = judge_prompt | llm | StrOutputParser()
        raw_judge = chain.invoke({"response": output})

        judgment = json.loads(raw_judge.strip().lstrip("```json").rstrip("```"))
        if not judgment.get("safe", True):
            return {
                **state,
                "blocked": True,
                "block_reason": f"Unsafe output: {judgment.get('reason')}",
                "block_stage": "output_guardrail"
            }
    except json.JSONDecodeError:
        print("[GUARDRAIL] Warning: Could not parse output judge response, blocking as fail-safe")
        return {
            **state,
            "blocked": True,
            "block_reason": "Output safety check could not validate the response",
            "block_stage": "output_guardrail"
        }
    except Exception as e:
        print(f"[GUARDRAIL] Error in output judge: {e}")
        return {
            **state,
            "blocked": True,
            "block_reason": f"Output guardrail error: {e}",
            "block_stage": "output_guardrail"
        }

    return {
        **state,
        "final_output": output
    }


# -------- Node 4: Reject --------
def reject_node(state: AgentState) -> AgentState:
    """Returns a polite rejection message."""
    return {
        **state,
        "final_output": (
            f"I'm sorry, I'm not able to help with that. "
            f"({state.get('block_reason', 'Request not allowed')})"
        )
    }


# -------- Node 5: Respond --------
def respond_node(state: AgentState) -> AgentState:
    """Final node — just passes the output through."""
    return state