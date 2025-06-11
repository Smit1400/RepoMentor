import streamlit as st
import datetime

from src.reminderAI.database.objects import Project
from src.reminderAI.database.utils import store_object_in_collection


def on_form_submit():
    project_object = Project(
        project_name=st.session_state.project_name,
        project_description=st.session_state.project_description,
        project_git=st.session_state.project_git,
        project_end_date=st.session_state.project_end_date.isoformat()
    )
    result = store_object_in_collection(project_object)
    if result:
        st.write("Saved Successfully!")


with st.form("add_project", clear_on_submit=True):
    st.write("Fill Details about the project.")
    st.text_input("Project Name", placeholder="Portfolio?", key="project_name")
    st.text_area(
        "Project Description",
        placeholder="Summarize whats the projects about and what will the end product look like.",
        key="project_description",
    )
    st.text_input(
        "GitHub Link", placeholder="Project github link to track", key="project_git"
    )
    st.date_input(
        "Enter desired project end date", datetime.date.today(), key="project_end_date"
    )

    submitted = st.form_submit_button(
        "Submit", use_container_width=True, type="primary", on_click=on_form_submit
    )

