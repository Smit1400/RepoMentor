import streamlit as st
from src.reminder_AI.database.objects import Project
from src.reminder_AI.database.connect import get_connection
from typing import List, Dict, Optional
from bson import ObjectId


@st.cache_resource
def init_connection():
    return get_connection()

client = init_connection()

def get_project_collection():
    client = init_connection()
    db = client["reminder"]
    return db["project_details"]

def store_object_in_collection(project: Project):
    collection = get_project_collection()
    collection.insert_one(project.model_dump(by_alias=True))
    return True

def get_all_projects() -> List[Dict]:
    collection = get_project_collection()
    return list(collection.find())

def get_project_by_id(project_id: str) -> Optional[Dict]:
    collection = get_project_collection()
    proj = collection.find_one({"_id": project_id})
    # If you want to keep returning a string, nothing else needs doing
    return proj

def get_project_id_by_vector_name(vector_name: str) -> Optional[str]:
    """
    Given the tail of a repo name (e.g. 'langchain' for 'langchain-ai/langchain'),
    return the MongoDB _id of the matching project document, or None if not found.
    """
    coll = get_project_collection()
    # find a repo_full_name ending in "/<vector_name>"
    doc = coll.find_one(
        {"project_git_repo": {"$regex": f"/{vector_name}$"}},
        {"_id": 1}
    )
    return str(doc["_id"]) if doc else None