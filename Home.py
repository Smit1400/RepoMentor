import streamlit as st
import pymongo
from pathlib import Path
import os
import sys

project_root = Path(os.getcwd())
sys.path.append(project_root)

from src.reminder_AI.database.connect import get_connection
from src.reminder_AI.langchain.rag import create_graph


if "graph" not in st.session_state:
    st.session_state.graph = create_graph()


result = st.session_state.graph.invoke({'question': 'Display the code of runfpgrowth in app.py file'})
# print(result['answer'])


# st.write(f'Context: {result["context"]}\n\n')
st.write(f'Answer: {result["answer"].content}')