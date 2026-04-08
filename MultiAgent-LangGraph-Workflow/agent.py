import os
from typing import TypedDict, List, Annotated, Literal
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain_core.runnables.graph import MermaidDrawMethod
from IPython.display import display, Image
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import TypedDict, List, Literal, Dict

model = ChatOllama(model="llama3.2:latest")

class State(TypedDict):
    text: str
    classification: str
    entities: Dict[str, List[str]]
    summary: str
    sentiment: Dict[str, str]
    
    
    

classification_prompt = PromptTemplate(
    input_variables=["text"],
    template="Classify the following text into one of the categories: News, Blog, Research, or Other.\n\nText:{text}\n\nCategory:"
)

class ClassificationOutput(BaseModel):
    message_type: Literal['News', 'Blog', 'Research', 'Other'] = Field(...,description="Classify if the message in to the any one the Literal.")

def classification_node(state: State):
    '''Classify the text into one of the categories: News, Blog, Research, or Other'''
    
    message = HumanMessage(content=classification_prompt.format(text=state["text"]))
    classification = model.with_structured_output(ClassificationOutput).invoke([message]).message_type
    return {"classification": classification}




    entity_extraction_prompt = PromptTemplate(
    input_variables=["text"],
    template="Extract named entities... Only include information that is clearly present in the text."
)

class EntitiesOutput(TypedDict):
    Person: List[str] = Field(..., description="List of people mentioned in the text")
    Organization: List[str] = Field(..., description="List of organizations mentioned in the text")
    Location: List[str] = Field(..., description="List of locations mentioned in the text")

def entity_extraction_node(state: State):
    '''Extract all the entities (Person, Organization, Location) from the text'''
    
    message = HumanMessage(content=entity_extraction_prompt.format(text=state["text"]))
    entities = model.with_structured_output(EntitiesOutput).invoke([message])
    return {"entities": entities}



entity_extraction_prompt = PromptTemplate(
    input_variables=["text"],
    template="Extract named entities... Only include information that is clearly present in the text."
)

class EntitiesOutput(TypedDict):
    Person: List[str] = Field(..., description="List of people mentioned in the text")
    Organization: List[str] = Field(..., description="List of organizations mentioned in the text")
    Location: List[str] = Field(..., description="List of locations mentioned in the text")




def entity_extraction_node(state: State):
    '''Extract all the entities (Person, Organization, Location) from the text'''
    
    message = HumanMessage(content=entity_extraction_prompt.format(text=state["text"]))
    entities = model.with_structured_output(EntitiesOutput).invoke([message])
    return {"entities": entities}




summarization_node_prompt = PromptTemplate(
    input_variables=["text"],
    template="Summarize the following text in one short sentence.\n\nText:{text}\n\nSummary:"
)

def summarization_node(state: State):
    '''Summarize the text in one short sentence'''

    message = HumanMessage(content=summarization_node_prompt.format(text=state["text"]))
    summary = model.invoke([message]).content.strip()
    return {"summary": summary}


sentiment_node_prompt = PromptTemplate(
    input_variables=["text"],
    template="Analyze the sentiment of the following text..."
)



class SentimentOutput(TypedDict):
    Sentiment: Literal['Positive', 'Negative', 'Neutral'] = Field(..., description="Classify the text into the any one of the class")
    Description: str = Field(..., description="Description aboyt the sentiment")

def sentiment_node(state: State):
    '''Analyze the sentiment of the text: Positive, Negative, or Neutral'''
    
    message = HumanMessage(content=sentiment_node_prompt.format(text=state["text"]))
    sentiment = model.with_structured_output(SentimentOutput).invoke([message])
    return {"sentiment": sentiment}




# Create our StateGraph
workflow = StateGraph(State)

# Add nodes to the graph
workflow.add_node("classification_node", classification_node)
workflow.add_node("entity_extraction", entity_extraction_node)
workflow.add_node("summarization", summarization_node)
workflow.add_node("sentiment_analysis", sentiment_node)

# Add edges to the graph
workflow.set_entry_point("classification_node")  # Set the entry point of the graph
workflow.add_edge("classification_node", "entity_extraction")
workflow.add_edge("entity_extraction", "summarization")
workflow.add_edge("summarization", "sentiment_analysis")
workflow.add_edge("sentiment_analysis", END)

# Compile the graph
app = workflow.compile()




sample_text = """ On Monday morning, Emma Johnson met with executives from GlobalTech Innovations at their headquarters in San Francisco.
The meeting focused on a new partnership between GlobalTech and EcoFuture Solutions, a startup based in Berlin.
Later that day, Emma attended a tech summit hosted by Stanford University, where she spoke alongside Dr. Carlos Mendes, a renowned AI researcher from São Paulo."""

state_input = {"text": sample_text}
result = app.invoke(state_input)

print("\n===== Classification =====")
print(result["classification"])
print("\n===== Entities =====")
for key, values in result["entities"].items():
    print(f"  {key}: {values}")
print("\n===== Summary =====")
print(result["summary"])
print("\n===== Sentiment =====")
for key, value in result["sentiment"].items():
    print(f"  {key}: {value}")