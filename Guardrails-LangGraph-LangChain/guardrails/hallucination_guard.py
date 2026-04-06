# guardrails/hallucination_guard.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dataclasses import dataclass
from typing import List
import json

@dataclass
class GroundingResult:
    is_grounded: bool
    confidence: float          # 0.0 to 1.0
    unsupported_claims: List[str]
    verdict: str

class HallucinationGuard:
    """
    Checks whether an LLM answer is grounded in the provided context documents.
    Uses an LLM-as-judge approach.
    """

    GROUNDING_PROMPT = ChatPromptTemplate.from_messages([
        ("system", """You are a hallucination detection system.

Your job: given a CONTEXT (retrieved documents) and an ANSWER, determine if every claim
in the answer is supported by the context.

Reply ONLY with this JSON:
{{
  "is_grounded": true or false,
  "confidence": 0.0 to 1.0,
  "unsupported_claims": ["list of claims not found in context"],
  "verdict": "one-sentence summary"
}}

Be strict. If a specific fact in the answer isn't in the context, list it as unsupported."""),
        ("human", """CONTEXT:
{context}

ANSWER:
{answer}

Is the answer grounded in the context?""")
    ])

    def __init__(self, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.chain = self.GROUNDING_PROMPT | self.llm | StrOutputParser()

    def check(self, answer: str, context_docs: List[str]) -> GroundingResult:
        context = "\n\n---\n\n".join(context_docs)
        raw = self.chain.invoke({"context": context, "answer": answer})

        try:
            clean = raw.strip().lstrip("```json").rstrip("```").strip()
            data = json.loads(clean)
            return GroundingResult(
                is_grounded=data["is_grounded"],
                confidence=float(data["confidence"]),
                unsupported_claims=data.get("unsupported_claims", []),
                verdict=data.get("verdict", "")
            )
        except Exception as e:
            # Fail safe — treat as not grounded if we can't parse
            return GroundingResult(
                is_grounded=False,
                confidence=0.0,
                unsupported_claims=["Parse error in guardrail"],
                verdict="Could not evaluate grounding"
            )


# --- Demo ---
if __name__ == "__main__":
    guard = HallucinationGuard()

    context = [
        """AcmeCorp Pro plan costs $49/month and includes unlimited projects,
        priority support, and up to 10 team members. Annual billing saves 20%.""",

        """The free plan is limited to 3 projects and does not include
        priority support or team collaboration features."""
    ]

    # This answer contains a hallucination
    bad_answer = """The Pro plan costs $49/month and supports up to 10 team members.
    It also includes a dedicated account manager and a 30-day free trial."""

    # This answer is grounded
    good_answer = """The Pro plan costs $49/month, includes unlimited projects,
    priority support, and supports up to 10 team members. Annual billing saves 20%."""

    for label, answer in [("HALLUCINATED", bad_answer), ("GROUNDED", good_answer)]:
        result = guard.check(answer, context)
        print(f"\n[{label}]")
        print(f"  Grounded   : {result.is_grounded}")
        print(f"  Confidence : {result.confidence:.0%}")
        print(f"  Unsupported: {result.unsupported_claims}")
        print(f"  Verdict    : {result.verdict}")