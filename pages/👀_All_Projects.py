import streamlit as st
from src.reminderAI.database.utils import get_all_projects



if "projects" not in st.session_state:
    st.session_state.projects = get_all_projects()

if st.button("Reload Projects"):
    del st.session_state.projects
    st.rerun()

# Convert _id to string for display
for project in st.session_state.projects:
    if "_id" in project and not isinstance(project["_id"], str):
        project["_id"] = str(project["_id"])

st.title("🗂️ Project Gallery")

if not st.session_state.projects:
    st.info("No projects found.")
else:
    cols = st.columns(3)

    for idx, project in enumerate(st.session_state.projects):
        col = cols[idx % 3]
        with col:
            st.markdown(f"""
            <div style='
                background-color: #f9f9f9;
                border-radius: 12px;
                padding: 16px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                margin-bottom: 16px;
            '>
                <h4>🎯 {project.get('project_name', '(No name)')}</h4>
                <p><strong>Description:</strong> {project.get('project_description', '')}</p>
                <p><strong>GitHub:</strong> <a href="{project.get('project_git', '')}" target="_blank">🔗 Link</a></p>
                <p><strong>End Date:</strong> {project.get('project_end_date', '')}</p>
                <p><strong>ID:</strong> {project.get('_id', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Project", key=f"view-{project['_id']}"):
                st.session_state.selected_project = project["_id"]
if "selected_project" in st.session_state:
    st.write(st.session_state.selected_project)
