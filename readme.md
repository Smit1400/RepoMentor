# 🧠 RepoMentor

An AI-powered Streamlit application that helps you **chat with GitHub repos**, **discover beginner-friendly issues**, and soon **track project progress, schedule reminders**, and **explore related work** using semantic search.

## 🚀 Features

- **🗨️ Chat with Repos** — Use natural language to ask questions about your project’s code and documentation.
- **🧑‍💻 First-Time Contributor Assistant** — Automatically ranks and summarizes the best beginner issues from GitHub.
- **📦 Multi-Repo Support** — Easily switch between multiple indexed repositories.
- **⚡ Smart Caching** — Fast, on-demand loading of issue summaries and search results.
- **🔍 (Upcoming) Semantic Search** — Find related projects or research papers using embeddings.
- **⏰ (Upcoming) Reminder System** — Schedule one-time or recurring reminders for projects or tasks.
- **📊 (Upcoming) Project Dashboard** — Visualize project timelines, due dates, and contribution activity.

## 🛠️ Tech Stack

| Component         | Technology                          |
|------------------|--------------------------------------|
| Web Framework     | [Streamlit](https://streamlit.io)   |
| LLM Orchestration | [LangChain](https://www.langchain.com) |
| Embeddings        | OpenAI (`text-embedding-3-large`)   |
| Vector Store      | FAISS (with pluggable support)      |
| Database          | MongoDB (for project metadata)      |
| Environment Mgmt  | `python-dotenv`                     |

## 💾 Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-username/repomentor.git
   cd repomentor
   ```

2. **Set up a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file based on the provided template:

   ```ini
   OPENAI_API_KEY=your_openai_key
   GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat
   ```

## ⚡ Usage

Launch the app:

```bash
streamlit run Home.py
```

Then open your browser at: [http://localhost:8501](http://localhost:8501)

### Core Pages

- **🧠 RepoMentor (Home)** — Discover beginner issues, see smart summaries, and chat with GitHub repos.
- **💬 Chat** — Ask technical questions about any indexed repository.
- **👀 Project Index** — Add or manage GitHub projects (automatically creates a vector store for chat).
- **(Coming Soon)** Search & Reminders — Semantic search and deadline tracking features.

## 🧪 Developer Notes

- **Vector Index Path**: Stored per repo in `issueDB/<repo_name>/`
- **MongoDB**: Stores `repo_full_name`, vector path, and `_id` for linking
- **Caching**: Enabled via `@st.cache_data` for fast, repeated queries
- **LLM**: Used for summarizing issues and enabling guided onboarding

## 🐛 Troubleshooting

- **Nothing loads?** Make sure your `.env` is set and `OPENAI_API_KEY` is valid.
- **GitHub issues return 0?** Check if the repo has `help wanted` or `good first issue` labels.
- **Chat not working?** Ensure the vector store for that repo was successfully built.

## 🤝 Contributing

We welcome contributions!

1. Fork this repo
2. Create your branch: `git checkout -b feature/YourFeature`
3. Commit your changes
4. Push and open a PR 🚀
---

> Built with ❤️ to help contributors find their path and repos find their people.
