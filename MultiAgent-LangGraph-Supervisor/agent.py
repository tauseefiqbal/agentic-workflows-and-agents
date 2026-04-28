wdef draft_and_revise(ticket):
    draft = draft_initial_response(ticket)
 
    for i in range(MAX_REVISIONS):
        evaluation = evaluate_draft(draft, ticket)
        if "PASS" in evaluation:
            return draft # Success!
        else:
            # Logic buried in loops, state passed manually
            draft = revise_based_on_feedback(draft, evaluation)
 
    return draft # Hope for the best


knowledge_base = [
    "For login issues, tell the user to try resetting their password via the 'Forgot Password' link.",
    "Billing inquiries should be escalated to the billing department by creating a ticket in Salesforce.",
    "The app is known to crash on startup if the user's cache is corrupted. The standard fix is to clear the application cache.",
]


from dataclasses import dataclass, field
from typing import Annotated, List, TypedDict
 
from IPython.display import Image, display
from langchain_ollama import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

llm = ChatOllama(model="qwen3:8b")

embeddings = FastEmbedEmbeddings()
vectorstore = InMemoryVectorStore.from_documents(
    [Document(page_content=text) for text in knowledge_base],
    embedding=embeddings,
)
retriever = vectorstore.as_retriever()


@dataclass
class TicketTriageState:
    ticket_text: str
    classification: str = ""
    retrieved_docs: List[Document] = field(default_factory=lambda: [])
    draft_response: str = ""
    evaluation_feedback: str = ""
    revision_count: int = 0


CLASSIFY_PROMPT = """
Classify this support ticket into one of the following categories:
'Technical Issue', 'Billing Inquiry', 'General Question'.
 
<ticket>
{ticket_text}
</ticket>
""".strip()
 
def classify_ticket(state: TicketTriageState) -> dict:
    classification = llm.invoke(CLASSIFY_PROMPT.format(ticket_text=state.ticket_text))
    return {"classification": classification.content}

def retrieve_knowledge(state: TicketTriageState) -> dict:
    retrieved_docs = retriever.invoke(state.ticket_text)
    return {"retrieved_docs": retrieved_docs}


DRAFT_PROMPT = """
Based on this context:
<context>
{context}
</context>
 
Draft a response for this ticket:
<ticket>
{ticket_text}
</ticket>
""".strip()
 
def draft_response(state: TicketTriageState) -> dict:
    context = "\n".join([doc.page_content for doc in state.retrieved_docs])
    prompt = DRAFT_PROMPT.format(context=context, ticket_text=state.ticket_text)
    draft = llm.invoke(prompt)
    return {"draft_response": draft.content}


EVALUATE_PROMPT = """
Does this draft
<draft>
{draft_response}
</draft>
 
fully address the ticket
 
<ticket>
{ticket_text}
</ticket>
 
If not, provide feedback.
Respond with 'PASS' or 'FAIL: [feedback]'."
""".strip()
 
def evaluate_draft(state: TicketTriageState) -> dict:
    evaluation_prompt = EVALUATE_PROMPT.format(
        draft_response=state.draft_response, ticket_text=state.ticket_text
    )
    evaluation_result = llm.invoke(evaluation_prompt)
    revision_count = state.revision_count + 1
    return {"evaluation_feedback": evaluation_result.content, "revision_count": revision_count}


REVISE_PROMPT = """
Revise this draft:
<draft>
{draft_response}
</draft>
 
based on the following feedback:
 
<feedback>
{evaluation_feedback}
</feedback>
""".strip()
 
def revise_response(state: TicketTriageState) -> dict:
    revised_draft = llm.invoke(
        REVISE_PROMPT.format(
            draft_response=state.draft_response,
            evaluation_feedback=state.evaluation_feedback,
        )
    )
    return {"draft_response": revised_draft.content}


graph = StateGraph(TicketTriageState)
 
# Add all our functions as nodes
graph.add_node("classify", classify_ticket)
graph.add_node("retrieve", retrieve_knowledge)
graph.add_node("draft", draft_response)
graph.add_node("evaluate", evaluate_draft)
graph.add_node("revise", revise_response)

# Define the main sequence of operations
graph.add_edge("classify", "retrieve")
graph.add_edge("retrieve", "draft")
graph.add_edge("draft", "evaluate")
 
# After revising, the draft must be evaluated again
graph.add_edge("revise", "evaluate")


def should_revise(state: TicketTriageState) -> str:
    feedback = state.evaluation_feedback
    revision_count = state.revision_count
    # If the draft failed evaluation and we haven't hit our revision limit, try again
    if "FAIL" in feedback and revision_count < 3:
        return "revise"
    # Otherwise, we're done
    else:
        return "end"
 
graph.add_conditional_edges(
    "evaluate",  # After evaluation...
    should_revise, # Ask this function what to do next
    {
        "revise": "revise", # Go back for another round
        "end": END,         # Or finish up
    },
)

graph.set_entry_point("classify")
app = graph.compile()



initial_state = TicketTriageState(ticket_text="My login is broken, please help!")
final_state = app.invoke(initial_state)

print("\n=== Classification ===")
print(final_state["classification"])
print("\n=== Draft Response ===")
print(final_state["draft_response"])
print("\n=== Evaluation ===")
print(final_state["evaluation_feedback"])
print(f"\nRevisions: {final_state['revision_count']}")


@tool
def classify_ticket(ticket_text: str) -> str:
    """
    Classifies a support ticket into 'Technical Issue', 'Billing Inquiry', or 'General Question'.
    Use this tool first to understand the nature of the ticket.
    """
    return llm.invoke(CLASSIFY_PROMPT.format(ticket_text=ticket_text)).content.strip()
 
 
@tool
def retrieve_knowledge(ticket_text: str) -> list[str]:
    """
    Retrieves relevant knowledge base articles for a given ticket.
    Use this for 'Technical Issue' tickets to find potential solutions.
    """
    return [doc.page_content for doc in retriever.invoke(ticket_text)]
 
 
@tool
def draft_response(ticket_text: str, context: list[str]) -> str:
    """
    Drafts a helpful response to a support ticket, using provided context.
    """
    context_str = "\n".join([doc for doc in context])
    return llm.invoke(
        DRAFT_PROMPT.format(context=context_str, ticket_text=ticket_text)
    ).content.strip()
 
 
tools = [classify_ticket, retrieve_knowledge, draft_response]

AGENT_SYSTEM_PROMPT = """
You are an expert support ticket triager. Your goal is to process a user's ticket by taking the following steps:
1. First, classify the ticket to understand its category.
2. If the ticket is a 'Technical Issue', retrieve relevant knowledge.
3. Finally, draft a response to the user.
You must use the provided tools to perform these actions in sequence. Respond ONLY with the final drafted response once all steps are complete.
"""

agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", AGENT_SYSTEM_PROMPT),
        ("placeholder", "{messages}"),
    ]
)
 
llm_with_tools = llm.bind_tools(tools)
agent = agent_prompt | llm_with_tools 