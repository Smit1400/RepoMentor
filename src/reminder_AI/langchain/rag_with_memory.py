from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, END
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
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

vector_store = FAISS.load_local(
    "C:/Users/shahs/Desktop/reminderAI/vectorDB/SmartCart_MBA", embeddings, allow_dangerous_deserialization=True
)

graph_builder = StateGraph(MessagesState)


@tool(response_format="content_and_artifact")
def retrieve(query: str):
    "Retreive information related to a query"
    docs = vector_store.similarity_search(query=query, k=5)
    serialized_docs = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in docs
    )
    return serialized_docs, docs

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or response"""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": response}

tools = ToolNode([retrieve])

def generate(state: MessagesState):
    """Generate Answer"""
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "assistant")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages
    response = llm.invoke(prompt)
    return {"messages": response}


graph_builder.add_node(query_or_respond)
graph_builder.add_node(tools)
graph_builder.add_node(generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges(
    "query_or_respond",
    tools_condition,
    {END: END, "tools": "tools"}
)
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)

def create_graph():
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)
    return graph