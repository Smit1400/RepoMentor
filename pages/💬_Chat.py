import streamlit as st
from src.reminder_AI.database.utils import get_project_by_id
from src.reminder_AI.langchain.rag_with_memory import build_graph
import os

if "proj_name" not in st.session_state:
    st.session_state.proj_name = "....."

project_id = st.session_state.get("selected_project")
if not project_id:
    st.switch_page("pages/👀_Project_Index.py")
    st.stop()

proj = get_project_by_id(project_id)
if proj and st.session_state.proj_name == ".....":
    st.session_state.proj_name = proj["project_name"]
    if "graph" not in st.session_state:
        with st.spinner("Loading Project Index to chat...", show_time=True):
            st.session_state.graph = build_graph(vector_store_path=os.path.join(os.getcwd(), *proj["project_index_path"]))
            print("Graph Loaded")
    st.rerun()

def process_message(message: str):
    config = {"configurable": {"thread_id": "abc123"}}
    inputs = {"messages": [{"role": "user", "content": message}]}
    result = st.session_state.graph.invoke(inputs, config=config)
    final_msg = result["messages"][-1]
    return {"type": "text", "content": f"Response: {final_msg.content}"}

def main():
    st.title(f"💬 Chat with {st.session_state.proj_name}")
    if "history" not in st.session_state:
        st.session_state.history = []

    user_input = st.chat_input("Your message...")
    if user_input:
        st.session_state.history.append(("user", user_input, "text"))
        result = process_message(user_input)
        st.session_state.history.append(("assistant", result["content"], result["type"]))

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