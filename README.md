# ⚡ TaskBot Pro — AI-Powered Task Management

> Manage your tasks through natural language. No forms. No buttons. Just conversation.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-Agent-green?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-LLM-orange?style=flat-square)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-darkgreen?style=flat-square&logo=supabase)
![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-red?style=flat-square&logo=streamlit)

---

## 🧠 What is TaskBot Pro?

TaskBot Pro is a production-deployed, multi-user task management system powered by a **LangChain SQL Agent**. Instead of clicking through a UI, users interact with their task database entirely through natural language.

```
"Add a task to review the PR"              → INSERT INTO tasks...
"Show me everything pending"               → SELECT * WHERE status = 'pending'...
"Mark the deployment task as complete"     → UPDATE tasks SET status = 'completed'...
```

The LLM understands intent, generates SQL, executes it against a live PostgreSQL database, and returns a clean formatted response — all in one conversational turn.

---

## 🏗️ Architecture

```
User Input (Natural Language)
        ↓
  Streamlit Frontend
        ↓
  LangChain SQL Agent (Groq LLM)
        ↓
  SQLDatabaseToolkit → SQL Query Generation
        ↓
  Supabase PostgreSQL (Cloud)
        ↓
  Formatted Markdown Response
```

---

## ✨ Features

- 💬 **Natural Language Interface** — create, read, update, delete tasks by just talking
- 🧠 **Conversational Memory** — LangGraph's `InMemorySaver` maintains context across multi-turn sessions
- 👥 **Multi-Tenant Isolation** — each user sees only their own data, enforced at DB level and LLM prompt level simultaneously
- 🔐 **Persistent Auth** — custom authentication system backed by Supabase with `bcrypt`-hashed passwords, survives every redeploy
- ☁️ **Production Deployed** — live on Streamlit Cloud with SSL, Session Pooler, and NullPool configuration
- 🎨 **Glassmorphism UI** — custom CSS-injected dark purple gradient interface

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (LLaMA / GPT-OSS) |
| Agent Framework | LangChain + LangGraph |
| Database | PostgreSQL via Supabase |
| ORM | SQLAlchemy + psycopg2 |
| Frontend | Streamlit |
| Auth | Custom (bcrypt + Supabase) |
| Deployment | Streamlit Cloud |

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/kkc0de/taskbot-pro.git
cd taskbot-pro
```

### 2. Create a virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root folder:
```env
DB_HOST=your-supabase-host
DB_PORT=6543
DB_USER=postgres.your-project-id
DB_PASSWORD=your-password
DB_NAME=postgres
GROQ_API_KEY=your-groq-api-key
```

### 5. Run the app
```bash
streamlit run SqlDatabase.py
```

---

## 🔐 Multi-Tenancy Design

User data isolation is enforced at **two layers**:

1. **Database level** — every task row has a `user_id` column. All queries include `WHERE user_id = '{username}'`
2. **LLM prompt level** — the system prompt hardcodes the logged-in user's ID, so the agent cannot query another user's data even if prompted to

This dual-layer approach ensures data leakage is impossible by design.

---

## 📁 Project Structure

```
taskbot-pro/
├── SqlDatabase.py       # Main app (agent + auth + UI)
├── requirements.txt     # Dependencies
├── .gitignore           # Excludes .env and auth config
└── README.md
```

---

## 🌐 Live Demo

> 🔗 https://taskbot-pro-mkurqckua3f2cksoaomh5t.streamlit.app/

---

## 📄 License

MIT License — feel free to fork and build on it.

---

<p align="center">Built by <a href="https://linkedin.com/in/krishna-kant-sharma-863649381">Krishna Kant Sharma</a></p>
