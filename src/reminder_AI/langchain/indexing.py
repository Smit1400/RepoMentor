from langchain_community.document_loaders import GithubFileLoader
from dotenv import load_dotenv
import os

import getpass
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

from uuid import uuid4

load_dotenv()

ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

GITHUB_API_URL = os.getenv("GITHUB_API_URL")

def load_github(repo_name: str, branch: str):
    loader = GithubFileLoader(
        repo=repo_name,
        branch=branch,
        access_token=ACCESS_TOKEN,
        github_api_url=GITHUB_API_URL,
        file_filter=lambda fp: fp.endswith((".py", ".md")),
    )
    documents = loader.load()
    vector_store(documents, repo_name)

def vector_store(documents, repo_name):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 2000,
        chunk_overlap = 500,
        separators= ["\n\n", "\n", " ", ""]
    )
    docs = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
    vector_store_object = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    uuids = [str(uuid4()) for _ in docs]
    vector_store_object.add_documents(documents=docs, ids=uuids)

    faiss_name = repo_name.split("/")[1]
    vector_store_object.save_local(f"vectorDB/{faiss_name}")