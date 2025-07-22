from functools import lru_cache
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 1) Set up your LLM — adjust temperature / model as needed
llm = init_chat_model(model="gpt-4o-mini", model_provider="openai")

# 2) Build a prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert Open-Source Maintainer. "
     "When given a GitHub issue, you produce a very short summary (2 sentences max) "
     "and 3–4 bullet points that guide the user how to get started fixing it—"
     "without giving away the full solution."
    ),
    ("human", 
     "Issue Title:\n{title}\n\n"
     "Issue Description:\n{body}\n\n"
     "Produce:\n"
     "1) A 2-sentence summary.\n"
     "2) A 3–4 item “Getting Started” list (give code if boiler code/links to understand if necessary).\n\n"
     "Output in markdown."
    ),
])

# 3) Cache summaries so you don’t double-bill
@lru_cache(maxsize=128)
def summarize_issue(title: str, body: str) -> str:
    messages = prompt.format_messages(title=title, body=body)
    response = llm(messages)
    print(response)
    return response.content

# 4) Put it all together: for each top doc, grab metadata + summary
def summarize_top_issues(top_docs: list[Document]) -> list[dict]:
    """
    top_docs: list of your LangChain Documents (metadata includes title/body/url)
    returns: list of dicts with keys: title, url, summary
    """
    # print(top_docs[0][0].metadata)
    outputs = []
    for doc in top_docs:
        md = doc[0].metadata
        summary_md = summarize_issue(md["title"], md["body"])
        outputs.append({
            "number":  md["number"],
            "title":   md["title"],
            "url":     md["url"],
            "summary": summary_md,
        })
    return outputs
