import streamlit as st
from src.reminder_AI.database.objects import Project
from Home import get_project_collection
import pymongo
from typing import List, Dict

def store_object_in_collection(project: Project):
    collection = get_project_collection()
    collection.insert_one(project.dict(by_alias=True))
    return True

def get_all_projects() -> List[Dict]:
    collection = get_project_collection()
    return list(collection.find())