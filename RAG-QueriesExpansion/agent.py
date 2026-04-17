from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ---- STEP 1: Keyword Extraction ----
keyword_prompt = ChatPromptTemplate.from_template("""
You will be given a query. Provide a maximum of 3 keywords from the given input query
Extract the most relevant keywords from the following query.
Return them as a comma-separated list without any extra text.

IMPORTANT:
- **Do not enumerate the keywords**.
- **Do not generate duplicate keywords**.
Example:
Input Query: "How to setup SSO?"
Keywords:
Answer: ["SSO", "Single Sign-On"]

Query: "{query}"
""")

keyword_chain = keyword_prompt | llm | StrOutputParser()

# ---- STEP 2: Query Expansion ----
expansion_prompt = ChatPromptTemplate.from_template("""
You are an assistant that generates query expansions.
Given a base query and a list of keywords, create {num_variations} 
natural-sounding variations of the query. Each variation should
incorporate at least one keyword in a meaningful way.

Base Query: "{query}"
Keywords: {keywords}

Output only the variations, one per line, without numbering.
""")

expansion_chain = expansion_prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0.7) | StrOutputParser()

# ---- Combine into a sequential pipeline ----
def run_query_expansion(inputs):
    query = inputs["query"]
    num_variations = inputs["num_variations"]
    keywords = keyword_chain.invoke({"query": query})
    expanded_queries = expansion_chain.invoke({"query": query, "num_variations": num_variations, "keywords": keywords})
    return {"keywords": keywords, "expanded_queries": expanded_queries}

result = run_query_expansion({
   "query": "How to optimize Python code for faster execution and lower memory usage?",
   "num_variations": 5
})
    
print("\nExtracted Keywords:", result["keywords"])
print("\nExpanded Queries:")
print(result["expanded_queries"])



from rank_bm25 import BM25Okapi
import nltk
from nltk.corpus import stopwords
import string

def extract_keywords_bm25(query: str, corpus: list, top_k: int = 5) -> list:
    stop_words = set(stopwords.words('english'))
    
    # Tokenize corpus
    tokenized_corpus = [
        [word.lower() for word in doc.split() if word.lower() not in stop_words and word not in string.punctuation]
        for doc in corpus
    ]
    
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Tokenize query
    tokenized_query = [word.lower() for word in query.split() if word.lower() not in stop_words]
    
    # Get BM25 scores
    scores = bm25.get_scores(tokenized_query)
    
    # Find top scoring document
    top_doc_idx = scores.argmax()
    top_doc_tokens = tokenized_corpus[top_doc_idx]
    
    # Return top_k unique keywords from top document
    keywords = list(dict.fromkeys(top_doc_tokens))[:top_k]
    return keywords


from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def expand_query_with_context(previous_messages: list, current_query: str, num_variations: int = 5) -> list:
    # Join previous messages into a context string
    conversation_context = "\n".join(previous_messages)
    
    prompt = f"""
    You are an assistant that generates query expansions for information retrieval systems.
    Use the previous conversation context to understand the topic and keep expansions relevant.
    Generate {num_variations} natural-sounding variations of the current query,
    incorporating synonyms, related phrases, or alternative wording.

    Conversation so far:
    {conversation_context}

    Current Query:
    "{current_query}"

    Output only the variations, one per line, without numbering or extra commentary.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for query expansion."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7 # Giving more freedom to the LLM to generate variation
    )

    # Extract and clean output
    variations_text = response.choices[0].message.content.strip()
    variations = [line.strip() for line in variations_text.split("\n") if line.strip()]

    return variations


previous_chats = [
    "User: I want to learn how to speed up Python code.",
    "Assistant: You can try profiling your code to find bottlenecks and optimize them.",
    "User: What about memory usage?"
]
    
latest_query = "How to optimize Python code for performance?"
    
expanded_queries = expand_query_with_context(previous_chats, latest_query, num_variations=5)
    
print("Expanded Queries:")
for q in expanded_queries:
    print("-", q)




from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize LLMs
hypo_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)       # Deterministic for hypothetical answer
expand_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)   # Creative for query expansion

# --- Step 1: Hypothetical Answer Generation ---
hypo_prompt = ChatPromptTemplate.from_template("""
You are an expert assistant. Given the following question,
generate a detailed and relevant hypothetical answer.

Question: "{query}"
""")

hypo_chain = hypo_prompt | hypo_llm | StrOutputParser()

# --- Step 2: Query Expansion using Hypothetical Answer as Context ---
expand_prompt = ChatPromptTemplate.from_template("""
You are a query expansion assistant.
Use the following hypothetical answer as context to generate {num_variations}
natural-sounding variations of the original query.
Incorporate synonyms, related terms, and rephrasings.

Hypothetical Answer:
{hypothetical_answer}

Original Query:
"{query}"

Output only the variations, one per line, without numbering or extra commentary.
""")

expand_chain = expand_prompt | expand_llm | StrOutputParser()

# --- Combine into a sequential pipeline ---
def run_hyde_expansion(inputs):
    query = inputs["query"]
    num_variations = inputs["num_variations"]
    hypothetical_answer = hypo_chain.invoke({"query": query})
    expanded_queries = expand_chain.invoke({"query": query, "num_variations": num_variations, "hypothetical_answer": hypothetical_answer})
    return {"hypothetical_answer": hypothetical_answer, "expanded_queries": expanded_queries}

query = "How to optimize Python code for faster execution and lower memory usage?"
result = run_hyde_expansion({
    "query": query,
    "num_variations": 5
})
    
print("\n--- Hypothetical Answer ---")
print(result["hypothetical_answer"])
print("\n--- Expanded Queries ---")
print(result["expanded_queries"])
