import streamlit as st
import pymongo
from pathlib import Path
import os
import sys

project_root = Path(os.getcwd())
sys.path.append(project_root)

from src.reminder_AI.database.connect import get_connection
from src.reminder_AI.langchain.rag_with_memory import build_graph
from src.reminder_AI.utils.issue_loader import rank_issues
from src.reminder_AI.utils.issue_solver import summarize_top_issues

@st.cache_resource
def init_connection():
    return get_connection()


def main():
    query = "help me get started with setting up the repo"
    top_3 = rank_issues(query)
    summaries = summarize_top_issues(top_docs=top_3)
    for issue in summaries:
        header = f"#{issue['number']}: {issue['title']}"
        with st.expander(header, expanded=False):
            st.markdown(issue["summary"])
            st.markdown(f"[🔗 View on GitHub]({issue['url']})")
            st.write("---")  # horizontal rule

if __name__ == "__main__":
    main()