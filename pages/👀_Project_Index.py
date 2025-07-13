import streamlit as st
from src.reminder_AI.database.utils import get_all_projects
from datetime import datetime

# Initialize or reload projects in session state
def load_projects():
    return get_all_projects()

if "projects" not in st.session_state:
    st.session_state.projects = load_projects()

if "selected_project" in st.session_state:
    st.session_state.selected_project = None

if st.button("Reload Projects"):
    st.session_state.projects = load_projects()
    st.rerun()

# Convert MongoDB _id to string for display
for proj in st.session_state.projects:
    if "_id" in proj and not isinstance(proj["_id"], str):
        proj["_id"] = str(proj["_id"])

projects = st.session_state.projects

if not projects:
    st.info("No projects found.")
else:
    # Header row
    hdr_cols = st.columns([3, 5, 3, 2, 2])
    hdr_cols[0].markdown("**Name**")
    hdr_cols[1].markdown("**Description**")
    hdr_cols[2].markdown("**GitHub URL**")
    hdr_cols[3].markdown("**End Date**")
    hdr_cols[4].markdown("**Action**")

    # Data rows
    for proj in projects:
        cols = st.columns([3, 5, 3, 2, 2])
        cols[0].write(proj.get('project_name', '(No name)'))
        cols[1].write(proj.get('project_description', ''))

        git_url = f'https://github.com/{proj.get("project_git_repo")}/tree/{proj.get("project_git_branch")}' if proj.get("project_git_repo") else None
        if git_url:
            cols[2].markdown(f"[🔗 Project Link]({git_url})")
        else:
            cols[2].write("-")

        end_date = proj.get('project_end_date', '')
        try:
            dt = datetime.strptime(end_date, "%Y-%m-%d")
            cols[3].write(dt.strftime('%b %d, %Y'))
        except:
            cols[3].write(end_date or "-")

        # ID and View button
        id_str = proj.get('_id', '')
        with cols[4]:
            # st.write(id_str)
            if st.button("Chat", key=f"chat_{id_str}"):
                st.session_state.selected_project = id_str
                st.switch_page("pages/💬_Chat.py")

# Display selected project ID if chosen
# if "selected_project" in st.session_state:
#     st.write(f"Selected project ID: {st.session_state.selected_project}")
