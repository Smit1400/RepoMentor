import asyncio
import streamlit as st
import datetime
import os

from src.reminderAI.database.objects import Project
from src.reminderAI.database.utils import store_object_in_collection
from src.reminderAI.langchain.indexing import load_github


def on_form_submit():
    load_github(st.session_state.project_git_repo, st.session_state.project_git_branch)

    project_object = Project(
        project_name=st.session_state.project_name,
        project_description=st.session_state.project_description,
        project_git_repo=st.session_state.project_git_repo,
        project_git_branch=st.session_state.project_git_branch,
        project_end_date=st.session_state.project_end_date.isoformat(),
    )
    if store_object_in_collection(project_object):
        st.success("Saved Successfully!")

with st.form("add_project", clear_on_submit=True):
    st.text_input("Project Name", key="project_name")
    st.text_area("Project Description", key="project_description")
    st.text_input("GitHub Repository Name (username/repo_name)", key="project_git_repo")
    st.text_input("GitHub Branch to Clone", key="project_git_branch")
    st.date_input("Desired project end date", datetime.date.today(), key="project_end_date")
    st.form_submit_button("Submit", on_click=on_form_submit)
