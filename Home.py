import streamlit as st
from pathlib import Path
import os
import sys

project_root = Path(os.getcwd())
sys.path.append(project_root)

from src.reminder_AI.utils.issue_loader import rank_issues
from src.reminder_AI.utils.issue_solver import summarize_top_issues
from src.reminder_AI.database.utils import get_project_id_by_vector_name

@st.cache_data(ttl=3600, show_spinner=False)
def load_summaries_for_repo(repo_choice: str, query: str):
    """Ranks and summarizes issues once per repo_choice+query combo."""
    top3 = rank_issues(query, index_path=repo_choice)
    return summarize_top_issues(top_docs=top3)

def main():
    st.title("🧠 RepoMentor")
    st.markdown(
        "Welcome to RepoMentor — your AI-powered guide to navigating GitHub projects. "
        "Find beginner-friendly issues and chat with any repo, instantly."
    )

    # 1) Repo picker
    repo_dirs = [
        d for d in os.listdir("issueDB")
        if os.path.isdir(os.path.join("issueDB", d))
    ]
    repo_choice = st.selectbox("Choose a repo to explore", repo_dirs)

    query = (
        "I’m new here—show me the top 3 beginner-friendly issues "
        "I can tackle to make a valuable contribution."
    )
    with st.spinner(f"Loading top issues for {repo_choice}…"):
        summaries = load_summaries_for_repo(repo_choice, query)

    # 2) Display only that repo’s issues
    for issue in summaries:
        header = f"#{issue['number']}: {issue['title']}"
        with st.expander(header):
            st.markdown(issue["summary"])
            st.markdown(f"[🔗 View on GitHub]({issue['url']})")
            st.write("---")


    if st.button(f"💬 Chat with {repo_choice}"):
        repo_id = get_project_id_by_vector_name(repo_choice)
        if not repo_id:
            st.switch_page("pages/👀_Project_Index.py")
        else:
            st.session_state.selected_project = repo_id
            st.switch_page("pages/💬_Chat.py")

if __name__ == "__main__":
    main()
