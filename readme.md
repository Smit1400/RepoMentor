# reminderAI

A Streamlit-based application that helps you track project progress, send timely reminders, and discover related projects or research papers using semantic search and AI.

## 🚀 Features

- **Interactive Chat Interface**: Converse with your projects and tasks (added).
- **Automated Reminders**: Schedule one-off or recurring reminders (todo).
- **Project Dashboard**: Visualize status, due dates, and progress (added).
- **Semantic Search**: Find similar projects or papers via embeddings & VectorDB (todo).
- **Pluggable Vector Store**: Supports FAISS, Pinecone, and other VectorDBs (currently faiss).
- **Background Loading & Caching**: Fast startup with cached document loaders (future task).

## 🛠️ Tech Stack

- **Language**: Python 3.9+
- **Web Framework**: Streamlit
- **LLM Orchestration**: LangChain / Langgraph
- **Vector Database**: FAISS
- **Embeddings**: OpenAI / Sentence Transformers
- **Env Management**: python-dotenv

## 💾 Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-username/reminderAI.git
   cd reminderAI
   ```

2. **Create & activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   - Copy `.env.example` to `.env`
   - Populate with your API keys and settings:
     ```ini
     OPENAI_API_KEY=your_openai_key
     ```

5. **Customize config (optional)**

   - Edit `config.yaml` for advanced settings (e.g., embedding model, reminder intervals).

## ⚡ Usage

```bash
streamlit run Home.py
```

- Open your browser at `http://localhost:8501`.
- Use the **Home** tab to interact with your projects and tasks.
- Visit **Add Project** for adding your project details
- Explore **Search** to find related projects or papers (to be added........)

## ⚙️ Configuration Details

- **.env**: Loaded via `python-dotenv` (`load_dotenv()` in `app.py`).
- **Caching**: Document loaders are decorated with `@st.cache_data` for faster reloads.

## 🐛 Troubleshooting

- **Slow File Loading**: Use async document loaders and increase cache TTL.
- **Ignoring Local Folders**: Add paths to `.gitignore` (e.g., `data/`, `venv/`).
- **Environment Issues**: Verify your `.env` and ensure `load_dotenv()` is called early in `app.py`.

## 🤝 Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m "Add some feature"`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

