import asyncio
import streamlit as st
import datetime
import os

from src.reminder_AI.database.objects import Project
from src.reminder_AI.database.utils import store_object_in_collection
from src.reminder_AI.langchain.indexing import load_github
from src.reminder_AI.utils.issue_loader import issues_to_vector_store

if "selected_project" in st.session_state:
    st.session_state.selected_project = None

def on_form_submit():
    index_path = load_github(st.session_state.project_git_repo, st.session_state.project_git_branch)
    index_path_list = index_path.split("/")
    project_object = Project(
        project_name=st.session_state.project_name,
        project_description=st.session_state.project_description,
        project_git_repo=st.session_state.project_git_repo,
        project_git_branch=st.session_state.project_git_branch,
        project_end_date=st.session_state.project_end_date.isoformat(),
        project_index_path=index_path_list
    )
    if store_object_in_collection(project_object) and issues_to_vector_store(st.session_state.project_git_repo):
        st.success("Saved Successfully!")

with st.form("add_project", clear_on_submit=True):
    st.text_input("Project Name", key="project_name")
    st.text_area("Project Description", key="project_description")
    st.text_input("GitHub Repository Name (username/repo_name)", key="project_git_repo")
    st.text_input("GitHub Branch to Clone", key="project_git_branch")
    st.date_input("Desired project end date", datetime.date.today(), key="project_end_date")
    st.form_submit_button("Submit", on_click=on_form_submit)
