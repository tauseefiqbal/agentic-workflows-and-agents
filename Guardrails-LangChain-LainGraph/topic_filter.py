# guardrails/topic_filter.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

class TopicCheckResult(BaseModel):
    allowed: bool
    reason: str

ALLOWED_TOPICS = [
    "product features",
    "billing and subscriptions",
    "technical support",
    "account management",
    "shipping and returns",
]

TOPIC_FILTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a topic classification guardrail for a customer support chatbot.

The chatbot is ONLY allowed to discuss:
{allowed_topics}

Evaluate the user's message. Reply ONLY with a JSON object:
{{
  "allowed": true or false,
  "reason": "brief explanation"
}}

Be strict. If the user asks about anything outside the allowed topics, return allowed=false."""),
    ("human", "{user_message}")
])

class TopicFilter:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.chain = TOPIC_FILTER_PROMPT | self.llm | StrOutputParser()
        self.allowed_topics = "\n".join(f"- {t}" for t in ALLOWED_TOPICS)

    def check(self, user_message: str) -> TopicCheckResult:
        import json
        raw = self.chain.invoke({
            "allowed_topics": self.allowed_topics,
            "user_message": user_message
        })
        try:
            # Strip markdown code fences if present
            clean = raw.strip().lstrip("```json").rstrip("```").strip()
            data = json.loads(clean)
            return TopicCheckResult(**data)
        except Exception:
            # Fail safe — if we can't parse, block the message
            return TopicCheckResult(allowed=False, reason="Guardrail parse error")

# --- Quick test ---
if __name__ == "__main__":
    filter = TopicFilter()

    tests = [
        "My order hasn't arrived yet, can you help?",
        "What's the capital of France?",
        "How do I cancel my subscription?",
        "Write me a poem about cats",
        "I'm getting a 500 error when I log in",
    ]

    for msg in tests:
        result = filter.check(msg)
        status = "PASS" if result.allowed else "BLOCK"
        print(f"[{status}] '{msg[:50]}' -> {result.reason}")
x