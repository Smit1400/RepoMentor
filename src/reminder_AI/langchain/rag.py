from dotenv import load_dotenv
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START
from typing_extensions import List, TypedDict
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import FAISS
import getpass
import os

load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

os.environ["LANGSMITH_TRACING"] = "true"
if not os.environ.get("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter Langsmith API key: ")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

system = SystemMessagePromptTemplate.from_template(
    "You are an AI assistant that answers questions based on provided context."
)
human = HumanMessagePromptTemplate.from_template(
    "Context:\n{context}\n\nQuestion: {question}\nPlease answer concisely."
)
prompt = ChatPromptTemplate.from_messages([system, human])

vector_store = FAISS.load_local(
    "C:/Users/shahs/Desktop/reminderAI/vectorDB/SmartCart_MBA", embeddings, allow_dangerous_deserialization=True
)

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"], k=10)
    return {'context': retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state['context'])
    messages_prompt = prompt.invoke({'question': state['question'], 'context': docs_content})
    response = llm.invoke(messages_prompt)
    return {'answer': response}

def create_graph():
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    return graph