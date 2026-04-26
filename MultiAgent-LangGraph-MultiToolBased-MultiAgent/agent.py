import json
import logging
import os
import sys
from html.parser import HTMLParser

# Ensure stdout/stderr can print Unicode (e.g. emoji) on Windows consoles
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
from operator import add
from typing import Annotated, Any, Callable

import requests
import wikipedia
from ddgs import DDGS
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)

logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("primp").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# --- Pydantic models ---

class PageSummary(BaseModel):
    page_title: str
    page_summary: str
    page_url: str


class SearchResponse(BaseModel):
    page_summaries: list[PageSummary]


class WikiSearchResult(BaseModel):
    titles: list[str]


class FullPage(BaseModel):
    page_title: str
    page_url: str
    content: str


class PageContent(BaseModel):
    url: str
    content: str


# --- HTML strip helper ---

class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.fed: list[str] = []

    def handle_data(self, d: str):
        self.fed.append(d)

    def get_data(self) -> str:
        return "".join(self.fed)


def strip_tags(html: str) -> str:
    s = _HTMLStripper()
    s.feed(html)
    return s.get_data()


# --- Tools ---

def search_duck_duck_go(search_query: str) -> SearchResponse:
    """
    Searches through DuckDuckGo pages.
    :param search_query: Query to send to DuckDuckGo search.
    Search for one item at a time even if it means calling the tool multiple times.
    :return: SearchResponse with page summaries.
    """
    max_results = 10

    with DDGS() as dd:
        results_generator = dd.text(search_query, max_results=max_results)

    return SearchResponse(
        page_summaries=[
            PageSummary(
                page_title=x["title"], page_summary=x["body"], page_url=x["href"]
            )
            for x in results_generator
        ]
    )


def search_wikipedia(search_query: str) -> WikiSearchResult:
    """
    Searches Wikipedia and returns a list of matching page titles.
    :param search_query: Query to search Wikipedia for.
    :return: WikiSearchResult with matching page titles.
    """
    results = wikipedia.search(search_query)
    return WikiSearchResult(titles=results)


def get_wikipedia_page(page_title: str, max_text_size: int = 4_000) -> FullPage:
    """
    Gets full content of a Wikipedia page.
    :param page_title: Make sure this page exists by calling search_wikipedia first.
    :param max_text_size: Maximum characters to return. Defaults to 4000.
    :return: FullPage with title, URL, and content.
    """
    page = wikipedia.page(title=page_title, auto_suggest=False)
    full_content = strip_tags(page.html())
    return FullPage(
        page_title=page.title,
        page_url=page.url,
        content=full_content[:max_text_size],
    )


def get_page_content(url: str, max_text_size: int = 4_000) -> PageContent:
    """
    Fetches and returns the text content of a web page.
    :param url: The URL of the page to fetch.
    :param max_text_size: Maximum characters to return. Defaults to 4000.
    :return: PageContent with URL and text content.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    content = strip_tags(response.text)
    return PageContent(url=url, content=content[:max_text_size])


# --- Agent state ---

class AgentState(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    messages: Annotated[list, add] = Field(default_factory=list)


SYSTEM_INSTRUCTION = (
    "You are a helpful agent that has access to different tools. Use them to answer "
    "the user's query if needed. Only use information from external sources that you "
    "can cite. You can use multiple tools before giving the final answer. If the tool "
    "response does not give an adequate response you can use the tools again with "
    "different inputs. Only respond when you can cite the source from one of your "
    "tools. Only answer 'I don't know' after you have exhausted all ways to use the "
    "tools to search for that information."
)


# --- Tool schemas (OpenAI function-calling format) ---

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_duck_duck_go",
            "description": "Searches DuckDuckGo for the given query and returns up to 10 page summaries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {"type": "string", "description": "Query to send to DuckDuckGo."}
                },
                "required": ["search_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Searches Wikipedia and returns a list of matching page titles.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {"type": "string", "description": "Query to search Wikipedia for."}
                },
                "required": ["search_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_wikipedia_page",
            "description": "Gets full content of a Wikipedia page. Call search_wikipedia first to confirm the title exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page_title": {"type": "string", "description": "Exact Wikipedia page title."}
                },
                "required": ["page_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_page_content",
            "description": "Fetches and returns the text content of a web page given its URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL of the page to fetch."}
                },
                "required": ["url"],
            },
        },
    },
]


# --- Agent ---

class ToolCallAgent:
    def __init__(self, tools: list[Callable], model_name: str = "openai/gpt-oss-20b"):
        self.model_name = model_name
        self.tools = tools
        self.tool_mapping = {tool.__name__: tool for tool in self.tools}
        self.system_message = {"role": "system", "content": SYSTEM_INSTRUCTION}
        self.graph = None
        self.build_agent()

    def call_llm(self, state: AgentState):
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[self.system_message] + state.messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        assistant_dict: dict[str, Any] = {"role": "assistant", "content": msg.content}
        if msg.tool_calls:
            assistant_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        return {"messages": [assistant_dict]}

    def use_tool(self, state: AgentState):
        last_message = state.messages[-1]
        tool_calls = last_message.get("tool_calls") or []
        tool_messages = []
        for tc in tool_calls:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"] or "{}")
            func = self.tool_mapping[name]
            try:
                result = func(**args)
                content = json.dumps(result.model_dump(mode="json"))
            except Exception as e:
                content = json.dumps({"error": str(e)})
            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "name": name,
                    "content": content,
                }
            )
        return {"messages": tool_messages}

    @staticmethod
    def should_we_stop(state: AgentState) -> str:
        last_message = state.messages[-1]
        if last_message.get("tool_calls"):
            return "use_tool"
        return END

    def build_agent(self):
        builder = StateGraph(AgentState)
        builder.add_node("call_llm", self.call_llm)
        builder.add_node("use_tool", self.use_tool)

        builder.add_edge(START, "call_llm")
        builder.add_conditional_edges("call_llm", self.should_we_stop)
        builder.add_edge("use_tool", "call_llm")
        self.graph = builder.compile()


if __name__ == "__main__":
    agent = ToolCallAgent(
        tools=[
            get_wikipedia_page,
            search_wikipedia,
            search_duck_duck_go,
            get_page_content,
        ]
    )

    initial_state = AgentState(
        messages=[
            {
                "role": "user",
                "content": (
                    "What is the number and season of the south park episode "
                    "where they get time traveling immigrants? Who was the "
                    "director of that episode? Where and when was he born? "
                    "Give me his wikipedia page link."
                ),
            }
        ]
    )

    output_state = agent.graph.invoke(initial_state)

    final_text = output_state["messages"][-1].get("content") or ""
    print("\n=== FINAL ANSWER ===")
    print(final_text)