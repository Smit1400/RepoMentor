import streamlit as st
from src.reminder_AI.database.objects import Project
from Home import init_connection
from typing import List, Dict, Optional
from bson import ObjectId

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