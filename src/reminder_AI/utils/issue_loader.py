from github import Github
import os
import logging
from typing import List, Dict
from dotenv import load_dotenv

import faiss
import getpass
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

from uuid import uuid4
from datetime import datetime, timezone
import math

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GITHUB_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
gh = Github(GITHUB_TOKEN)

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

def fetch_beginner_issues(repo_full_name) -> List[Dict]:
    """
    Returns a list of dicts for all open issues in `repo_full_name`
    labeled either 'good first issue' or 'help wanted'.
    """
    repo = gh.get_repo(repo_full_name)
    target_labels = ["good first issue", "help wanted"]
    seen = {}

    for label in target_labels:
        # this call returns issues with *that one* label
        for issue in repo.get_issues(state="open", labels=[label]):
            seen[issue.id] = issue  # dedupe on issue.id

    results = []
    for issue in seen.values():
        results.append({
            "number":     issue.number,
            "title":      issue.title,
            "labels":     [lbl.name for lbl in issue.labels],
            "created_at": issue.created_at.isoformat(),
            "comments":   issue.comments,
            "body": issue.body or "",
            "url":        issue.html_url,
        })
    return results

def create_documents(issues):
    documents = []
    for issue in issues:
        page_content = f"\nGit Issue title: {issue['title']}\n\nIssue body: {issue['body']}\n"
        documents.append(Document(page_content=page_content, metadata = issue))

    return documents

def document_to_vector_store(documents, repo_full_name):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )

    uuids = [str(uuid4()) for _ in documents]
    vector_store.add_documents(documents=documents, ids = uuids)
    vector_store.save_local(f"issueDB/{repo_full_name.split('/')[1]}")


def issues_to_vector_store(repo_full_name: str = "langchain-ai/langchain"):
    issues = fetch_beginner_issues(repo_full_name)
    issues_to_docs = create_documents(issues)
    document_to_vector_store(issues_to_docs, repo_full_name)

    return True


def rank_issues(
    query: str,
    index_path: str,
    top_k: int = 4,
    alpha: float = 0.7,   # weight for semantic similarity
    beta: float = 0.2,    # weight for recency
    gamma: float = 0.1    # weight for comment activity
):
    """Returns a list of (Document, combined_score), sorted desc—and we'll take top 3."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vs = FAISS.load_local(folder_path=f"issueDB/{index_path}", embeddings=embeddings, allow_dangerous_deserialization=True)

    # 3) Semantic search → [(doc, sem_score), …]
    hits = vs.similarity_search_with_score(query, k=top_k)

    # 4) Normalize semantic scores to [0,1]
    sem_scores = [score for (_, score) in hits]
    min_s, max_s = min(sem_scores), max(sem_scores)
    norm_sem = [ (s - min_s) / (max_s - min_s + 1e-8) for s in sem_scores ]

    # 5) Build freshness scores: 1 / (days_since + 1)
    now = datetime.now(timezone.utc)
    freshness = []
    for doc, _ in hits:
        # print(doc)
        # created = datetime.fromisoformat(doc.metadata["created_at"])
        created_at = doc.metadata["created_at"]
        if isinstance(created_at, str):
            created = datetime.fromisoformat(created_at)
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
        else:
            created = created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
        days = (now - created).days
        freshness.append(1.0 / (days + 1))
    max_f = max(freshness)
    norm_fresh = [ f / max_f for f in freshness ]

    # 6) Activity score: log(comments+1), normalized
    comments = [doc.metadata["comments"] for (doc, _) in hits]
    log_comm = [math.log(c + 1) for c in comments]
    max_lc = max(log_comm) if log_comm else 1.0
    norm_comm = [ lc / max_lc for lc in log_comm ]

    # 7) Combine & sort
    combined = []
    for i, (doc, _) in enumerate(hits):
        score = alpha * norm_sem[i] + beta * norm_fresh[i] + gamma * norm_comm[i]
        combined.append((doc, score))
    combined.sort(key=lambda x: x[1], reverse=True)

    # Return top 3
    return combined[:3]