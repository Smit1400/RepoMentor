import pymongo
import streamlit as st

def get_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])
