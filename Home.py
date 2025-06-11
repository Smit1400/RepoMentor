import streamlit as st
import pymongo
from pathlib import Path
import os
import sys

project_root = Path(os.getcwd())
sys.path.append(project_root)

from src.reminderAI.database.connect import get_connection


@st.cache_resource
def init_connection():
    return get_connection()


client = init_connection()

def get_project_collection():
    client = init_connection()
    db = client["reminder"]
    return db["project_details"]

@st.cache_data(ttl=600)
def get_data():
    db = client.reminder
    items = db.project_details.find()
    items = list(items)  # make hashable for st.cache_data
    return items


items = get_data()

for item in items:
    st.write(item.get("_id"))
