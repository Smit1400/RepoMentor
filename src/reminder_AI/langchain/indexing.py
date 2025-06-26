from langchain_community.document_loaders import GithubFileLoader
from dotenv import load_dotenv
import os

import getpass
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from uuid import uuid4

load_dotenv()

ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

def load_github(repo_name: str, branch: str):
    loader = GithubFileLoader(
        repo=repo_name,
        branch=branch,
        access_token=ACCESS_TOKEN,
        github_api_url="https://api.github.com",
        file_filter=lambda fp: fp.endswith((".py", ".md")),
    )
    documents = loader.load()
    vector_store(documents, repo_name)

def vector_store(documents, repo_name):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
    vector_store_object = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store_object.add_documents(documents=documents, ids=uuids)
    results = vector_store_object.similarity_search(
        "What is SmartCart MBA all about?",
        k=1,
    )
    for res in results:
        print(res.page_content)
    faiss_name = repo_name.split("/")[1]
    vector_store_object.save_local(f"vectorDB/{faiss_name}")