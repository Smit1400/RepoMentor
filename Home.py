import streamlit as st
import pymongo
from pathlib import Path
import os
import sys

project_root = Path(os.getcwd())
sys.path.append(project_root)

from src.reminder_AI.database.connect import get_connection
from src.reminder_AI.langchain.rag_with_memory import create_graph


if "graph" not in st.session_state:
    st.session_state.graph = create_graph()

def process_message(message: str):
    config = {"configurable": {"thread_id": "abc123"}}
    inputs = {"messages": [{"role": "user", "content": message}]}
    result = st.session_state.graph.invoke(inputs, config=config)
    final_msg = result["messages"][-1]
    return {"type": "text", "content": f"Response: {final_msg.content}"}

def main():
    st.set_page_config(page_title="Chat Interface", layout="wide")
    st.title("💬 ReminderAI")

    if "history" not in st.session_state:
        st.session_state.history = []  # list of (role, content, type)

    # User input
    user_input = st.chat_input("Your message...")
    if user_input:
        # Append user message
        st.session_state.history.append(("user", user_input, "text"))
        # Process
        result = process_message(user_input)
        # Append bot response
        st.session_state.history.append(("assistant", result["content"], result["type"]))

    # Display chat history
    for role, content, ctype in st.session_state.history:
        if role == "user":
            st.chat_message("user").write(content)
        else:
            msg = st.chat_message("assistant")
            if ctype == "text":
                msg.write(content)
            else:
                msg.code(content, language="python")

if __name__ == "__main__":
    main()