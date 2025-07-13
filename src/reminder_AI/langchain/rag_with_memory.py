import os
import getpass
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

from langgraph.graph import StateGraph, MessagesState, END
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _ensure_api_keys():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API key: ")
    if not os.getenv("LANGSMITH_API_KEY"):
        os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Langsmith API key: ")
    # optional: validate keys here


def _init_vector_store(path: str, embedding_model: str) -> FAISS:
    """
    Load (or build) a FAISS vector store from the given local path.
    """
    embeddings = OpenAIEmbeddings(model=embedding_model)
    vs_path = Path(path)
    if not vs_path.exists():
        raise FileNotFoundError(f"Vector store not found at {path}")
    return FAISS.load_local(
        str(vs_path),
        embeddings,
        allow_dangerous_deserialization=True
    )


def build_graph(
    vector_store_path: str = "C:/Users/shahs/Desktop/reminderAI/vectorDB/SmartCart_MBA",
    embedding_model: str = "text-embedding-3-large",
    llm_name: str = "gpt-4o-mini",
    llm_provider: str = "openai",
    retrieval_k: int = 5
):
    """
    Initialize API keys, LLM, vector store, and assemble the LangGraph.
    Returns a compiled graph you can immediately run.
    """

    # 1) Ensure keys
    _ensure_api_keys()
    os.environ["LANGSMITH_TRACING"] = "true"

    # 2) Build LLM + embeddings + vector store
    logger.info("Initializing embeddings and LLM…")
    llm = init_chat_model(llm_name, model_provider=llm_provider)
    store = _init_vector_store(vector_store_path, embedding_model)

    # 3) Build the graph structure
    logger.info("Constructing graph nodes…")
    graph_builder = StateGraph(MessagesState)

    @tool(response_format="content_and_artifact")
    def retrieve(query: str):
        """Retrieve related docs from FAISS."""
        docs = store.similarity_search(query=query, k=retrieval_k)
        serialized = "\n\n".join(
            f"Source: {doc.metadata}\nContent: {doc.page_content}"
            for doc in docs
        )
        return serialized, docs

    def query_or_respond(state: MessagesState):
        """Generate tool call for retrieval or response"""
        llm_with_tools = llm.bind_tools([retrieve])
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": response}

    tools = ToolNode([retrieve])

    def generate(state: MessagesState):
        """Generate Answer"""
        recent = []
        for msg in reversed(state["messages"]):
            if msg.type == "tool":
                recent.append(msg)
            else:
                break
        recent = recent[::-1]
        docs_content = "\n\n".join(m.content for m in recent)

        system_prompt = (
            "You are an assistant for Q&A tasks. Use the retrieved context "
            "to answer briefly (max 3 sentences). If you don’t know, say so."
            f"\n\n{docs_content}"
        )

        # filter out pure-tool messages for the conversation
        convo = [
            m for m in state["messages"]
            if m.type in ("human", "assistant")
            or (m.type == "ai" and not m.tool_calls)
        ]

        prompt = [SystemMessage(system_prompt)] + convo
        response = llm.invoke(prompt)
        return {"messages": response}

    # wire up graph
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

    # compile with memory
    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    logger.info("Graph built and ready!")
    return graph
