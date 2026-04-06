# guardrails/schema_guard.py

from pydantic import BaseModel, ValidationError
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Type, TypeVar, Optional
import json

T = TypeVar("T", bound=BaseModel)

class SchemaGuard:
    """
    Validates LLM JSON output against a Pydantic schema.
    On failure, retries with a correction prompt (up to max_retries).
    """

    CORRECTION_PROMPT = ChatPromptTemplate.from_messages([
        ("system", "You are a JSON correction assistant. Fix the JSON to match the schema. Reply with ONLY valid JSON, no markdown."),
        ("human", """Schema:
{schema}

Invalid JSON:
{bad_json}

Validation error:
{error}

Return the corrected JSON:""")
    ])

    def __init__(self, model: str = "gpt-4o-mini", max_retries: int = 2):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.chain = self.CORRECTION_PROMPT | self.llm | StrOutputParser()
        self.max_retries = max_retries

    def _try_parse(self, text: str, schema: Type[T]) -> tuple[Optional[T], Optional[str]]:
        """Try to parse and validate. Returns (instance, error_message)."""
        try:
            clean = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(clean)
            return schema(**data), None
        except json.JSONDecodeError as e:
            return None, f"Invalid JSON: {e}"
        except ValidationError as e:
            return None, str(e)

    def validate(self, raw_output: str, schema: Type[T]) -> tuple[Optional[T], bool]:
        """
        Validate output against schema. Returns (parsed_object, was_corrected).
        Returns (None, False) if validation fails after all retries.
        """
        instance, error = self._try_parse(raw_output, schema)
        if instance:
            return instance, False

        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        current = raw_output

        for attempt in range(self.max_retries):
            print(f"[SCHEMA GUARD] Validation failed, retry {attempt+1}/{self.max_retries}: {error[:80]}")
            corrected = self.chain.invoke({
                "schema": schema_json,
                "bad_json": current,
                "error": error
            })
            instance, error = self._try_parse(corrected, schema)
            if instance:
                return instance, True
            current = corrected

        print(f"[SCHEMA GUARD] Failed after {self.max_retries} retries.")
        return None, False


# --- Example Schema ---
class ProductRecommendation(BaseModel):
    product_name: str
    price_usd: float
    in_stock: bool
    reason: str
    rating: float  # must be 0.0 to 5.0

# --- Demo ---
if __name__ == "__main__":
    guard = SchemaGuard()

    # Simulated bad LLM output
    bad_outputs = [
        # Missing field, wrong type
        '```json\n{"product_name": "AcmePro", "price_usd": "49 dollars", "reason": "Best value"}\n```',
        # Trailing comma (invalid JSON)
        '{"product_name": "AcmeLite", "price_usd": 9.99, "in_stock": true, "reason": "Budget pick", "rating": 4.2,}',
    ]

    for bad in bad_outputs:
        result, was_corrected = guard.validate(bad, ProductRecommendation)
        if result:
            print(f"\nParsed: {result}")
            print(f"Was auto-corrected: {was_corrected}")
        else:
            print(f"\nFailed to parse even after retries.")