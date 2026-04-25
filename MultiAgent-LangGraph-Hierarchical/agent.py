import os
import operator
from typing import TypedDict, Annotated, Literal

import finnhub
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

load_dotenv()


def get_llm(provider='groq'):
    return ChatGroq(model="llama-3.3-70b-versatile")


def create_agent(model, tools, system_prompt):
    return create_react_agent(model, tools, prompt=system_prompt)


router_llm = get_llm(provider='groq')

course_recommender_agent = create_agent(
    model=router_llm,
    tools=[],
    system_prompt="You are a course recommender. Based on the course catalog provided, recommend the best courses."
)

institution_recommender_agent = create_agent(
    model=router_llm,
    tools=[],
    system_prompt="You are an institution recommender. Based on the institution catalog provided, recommend the best institutions."
)


@tool
def get_stock_data(symbol: str):
    """Get Stock information for symbol."""
    api_key = os.environ["STOCK_API_KEY"]
    finnhub_client = finnhub.Client(api_key=api_key)
    
    data = finnhub_client.quote('AAPL')
    
    return data




@tool
def recommender_agent(user_query: str):
    """Returns recommendation of courses and institutions based on user query"""
    
    return invoke_recommender(user_query)




llm = get_llm(provider='groq')

main_agent = create_agent(
    model=llm, 
    tools=[get_stock_data, recommender_agent],
    system_prompt=(
                 "You are a helpful personal assistant. "
                 "You can tell the price of a stock and recommend courses and institutions. "
                 "Break down user requests into appropriate tool calls and coordinate the results. "
                 "When a request involves multiple actions, use multiple tools in sequence."
    )
)



@tool
def get_course_catalog(user_query: str):
    """Returns a list of curated courses from the catalog along with hash tags, course specification details"""
    courses = {
       "Beginners course on System Design": {
            "specs": "10-hour video series covering Load Balancers, Caching, and Database Sharding. Includes 5 hands-on projects.",
            "tags": ["#SystemDesign", "#SoftwareEngineering", "#Scalability"]
        },
        "Architecting Scalable systems": {
            "specs": "Advanced workshop focusing on Microservices, Event-driven architecture, and Multi-region deployment.",
            "tags": ["#Architecture", "#Microservices", "#CloudComputing"]
        },
        "Programming Best practices": {
            "specs": "Interactive coding labs teaching SOLID principles, Clean Code, and Unit Testing across multiple languages.",
            "tags": ["#CleanCode", "#SOLID", "#Programming"]
        },
        "Programming for Beginners": {
            "specs": "Interactive coding labs teaching fundamentals of Programming in Python.",
            "tags": ["#Programming Basics", "#Algorithms", "#Programming"]
        }
    }
    return courses



def invoke_course_agent(state):
    result = course_recommender_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    
    ai_msg = result["messages"][-1].content
    return {"results": [{"source": "course_agent", "result": result["messages"][-1].content}]}

# Institution Recommender Agent/Tool


@tool
def get_institution_catalog(user_query: str):
    """Returns a list of curated institutions who offer masters courses for working professionals"""
    colleges = {
       "Georgia Tech University": {
            "specs": "Online Masters in Artificial Intelligence, Machine Learning, Software Engineering. Highly Ranked amongst online masters.",
            "country": ["US"]
        },
         "Liverpool University": {
            "specs": "Online Masters in Artificial Intelligence, Machine Learning, Cyber Security",
            "country": ["UK"]
        },
        "Texas University": {
            "specs": "Online Masters in Machine Learning, Software Engineering",
            "country": ["US"]
        },
        "Illinois University": {
            "specs": "Online Masters in Artificial Intelligence, Machine Learning",
            "country": ["US"]
        },
    }
    return colleges



def invoke_institution_agent(state):
    result = institution_recommender_agent.invoke({"messages": [{"role": "user", "content": state["query"]}]})
    ai_msg = result["messages"][-1].content
    return {"results": [{"source": "institution_agent", "result": result["messages"][-1].content}]}




class AgentInput(TypedDict):
    """Simple input state for each subagent."""
    query: str


class AgentOutput(TypedDict):
    """Output from each subagent."""
    source: str
    result: str


class Classification(TypedDict):
    """A single routing decision: which agent to call with what query."""
    source: Literal["course_agent", "institution_agent"]
    query: str

class RouterState(TypedDict):
    query: str
    classifications: list[Classification]
    results: Annotated[list[AgentOutput], operator.add]  # Reducer collects parallel results
    final_answer: str


class ClassificationResult(BaseModel):
    """Result of classifying a user query into agent-specific sub-questions."""
    classifications: list[Classification] = Field(
        description="List of agents to invoke with their targeted sub-questions"
    )
    
    
def classify_query(state: RouterState) -> dict:
    """Classify query and determine which agents to invoke."""
    structured_llm = router_llm.with_structured_output(ClassificationResult)

    result = structured_llm.invoke([
        {
            "role": "system",
            "content": """Analyze this query and determine which knowledge bases to consult.
For each relevant source, generate a targeted sub-question optimized for that source.

Available sources:
- course_recommender_agent: Recommends a course based on user query
- institution_recommender_agent: Recommends a institution based on user query

Return ONLY the sources that are relevant to the query. Each source should have
a targeted sub-question optimized for that specific knowledge domain.
"""
        },
        {"role": "user", "content": state["query"]}
    ])

    return {"classifications": result.classifications}






def route_to_agents(state: RouterState) -> list[Send]:
    """Fan out to agents based on classifications."""
    return [
        Send(c["source"], {"query": c["query"]})
        for c in state["classifications"]
    ]
    


def synthesize_results(state: RouterState) -> dict:
    """Combine results from all agents into a coherent answer."""
    if not state["results"]:
        return {"final_answer": "No results found from any knowledge source."}

    formatted = [
        f"**From {r['source'].title()}:**\n{r['result']}"
        for r in state["results"]
    ]

    synthesis_response = router_llm.invoke([
        {
            "role": "system",
            "content": f"""Synthesize these search results to answer the original question: "{state['query']}"

- Combine information from multiple sources without redundancy
- Highlight the most relevant and actionable information
- Note any discrepancies between sources
- Keep the response concise and well-organized"""
        },
        {"role": "user", "content": "\n\n".join(formatted)}
    ])

    return {"final_answer": synthesis_response.content}




def build_graph():

    # --- Build the Graph ---
    workflow = StateGraph(RouterState)
    workflow.add_node("classify", classify_query) # Adds the new router agent to the flow
    workflow.add_node("course_agent", invoke_course_agent)
    workflow.add_node("institution_agent", invoke_institution_agent) # Adds the institution agent to the flow
    workflow.add_node("synthesize", synthesize_results)
    workflow.add_edge(START, "classify")
    workflow.add_conditional_edges("classify", route_to_agents, ["course_agent", "institution_agent"])
    workflow.add_edge("course_agent", "synthesize")
    workflow.add_edge("institution_agent", "synthesize")
    workflow.add_edge("synthesize", END)

    app = workflow.compile()
    return app


def invoke_recommender(user_query: str):
    app = build_graph()
    result = app.invoke({
        "query": user_query
    })
    print('--------------response from recommender-----------')
    print(result)
    return result



query = "Suggest a good college for masters in security"
for step in main_agent.stream(
    {"messages": [{"role": "user", "content": query}]}
):
    for update in step.values():
        for message in update.get("messages", []):
            message.pretty_print()