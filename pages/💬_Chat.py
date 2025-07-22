import streamlit as st
from src.reminder_AI.database.utils import get_project_by_id
from src.reminder_AI.langchain.rag_with_memory import build_graph
import os

# 1) One-time initialization
if "proj_name" not in st.session_state:
    st.session_state.proj_name = None

if "previous_project_id" not in st.session_state:
    st.session_state.previous_project_id = None

project_id = st.session_state.get("selected_project")

# 2) No project? Bounce back to index
if not project_id:
    st.switch_page("pages/👀_Project_Index.py")
    st.stop()

# 3) If the project ID changed, reload the graph & name
if project_id != st.session_state.previous_project_id:
    proj = get_project_by_id(project_id)
    st.session_state.proj_name = proj["project_name"]

    with st.spinner(f"Loading «{st.session_state.proj_name}»…"):
        st.session_state.graph = build_graph(
            vector_store_path=os.path.join(os.getcwd(), *proj["project_index_path"])
        )

    st.session_state.previous_project_id = project_id
    # No need for st.rerun() here!

# From here on out, st.session_state.graph and proj_name are always set
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

    user_input = st.chat_input("Your message…")
    if user_input:
        st.session_state.history.append(("user", user_input, "text"))
        reply = process_message(user_input)
        st.session_state.history.append(("assistant", reply["content"], reply["type"]))

    for role, content, ctype in st.session_state.history:
        bubble = st.chat_message(role)
        if ctype == "text":
            bubble.write(content)
        else:
            bubble.code(content, language="python")

if __name__ == "__main__":
    main()
