import os
from dotenv import load_dotenv
load_dotenv()

from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

docs = [
    Document(page_content="To reset your API key, go to settings > security."),
    Document(page_content="Our platform integrates with Slack, Teams, and Zoom."),
    Document(page_content="401 errors usually mean invalid API credentials.")
]

# Split into chunks
splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
texts = splitter.split_documents(docs)

# Create embeddings and FAISS index
embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(texts, embeddings)

retriever = db.as_retriever()




from langchain_classic.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain_classic.memory import ConversationBufferMemory

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory
)


query1 = "How do I reset my API key?"
print(qa_chain.run(query1))

query2 = "Does your platform work with Slack?"
print(qa_chain.run(query2))

query3 = "Why do I see a 401 error?"
print(qa_chain.run(query3))

query4 = "Can you remind me what we discussed earlier?"
print(qa_chain.run(query4))






