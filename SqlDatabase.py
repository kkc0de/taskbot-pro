import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
import urllib.parse
from sqlalchemy.pool import NullPool

if hasattr(st, "secrets") and len(st.secrets) > 0:
    os.environ.update(st.secrets)


# Page Formatting
st.set_page_config(
    page_title="TaskBot Pro | SQL Intelligence",
    page_icon="⚡",
    layout="wide"
)

# Google Fonts

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
""",unsafe_allow_html=True)

# Glassmorphism CSS

st.markdown("""
<style>
:root {
    --purple: #8b5cf6;
    --purple-light: #a78bfa;
    --cyan: #22d3ee;
    --glass: rgba(255,255,255,0.04);
    --glass-border: rgba(255,255,255,0.08);
    --text: #f1f0ff;
    --muted: rgba(255,255,255,0.4);
}
.stApp {
    background: #0d0118 !important;
    background-image:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(139,92,246,0.25) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(34,211,238,0.15) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 60% 20%, rgba(244,114,182,0.12) 0%, transparent 50%) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #f1f0ff !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem !important; max-width: 1100px !important; }
.stApp, .stApp p, .stApp label, .stApp div { color: #f1f0ff !important; font-family: 'DM Sans', sans-serif !important; }
 
/* ── Auth form styling ── */
.stTextInput input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #f1f0ff !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus {
    border-color: rgba(139,92,246,0.5) !important;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.15) !important;
}
.stButton button {
    background: linear-gradient(135deg, #8b5cf6, #22d3ee) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.5rem 2rem !important;
    width: 100% !important;
}
.stButton button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
 
/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    backdrop-filter: blur(12px) !important;
}
[data-testid="metric-container"]:hover { border-color: rgba(139,92,246,0.4) !important; transform: translateY(-2px) !important; }
[data-testid="metric-container"] label { font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important; color: rgba(255,255,255,0.4) !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: 500 !important; color: #f1f0ff !important; }
 
/* ── Alert box ── */
.stAlert { background: rgba(139,92,246,0.08) !important; border: 1px solid rgba(139,92,246,0.25) !important; border-radius: 12px !important; color: rgba(255,255,255,0.6) !important; }
 
/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
    backdrop-filter: blur(8px) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    border-color: rgba(139,92,246,0.25) !important;
    background: rgba(139,92,246,0.06) !important;
}
 
/* ── Tables ── */
table { width: 100% !important; border-collapse: collapse !important; font-size: 0.82rem !important; margin-top: 10px !important; }
thead tr th { padding: 8px 14px !important; text-align: left !important; color: #a78bfa !important; font-size: 10px !important; letter-spacing: 2px !important; text-transform: uppercase !important; border-bottom: 1px solid rgba(139,92,246,0.3) !important; background: transparent !important; }
tbody tr td { padding: 8px 14px !important; border-bottom: 1px solid rgba(255,255,255,0.05) !important; color: #f1f0ff !important; }
tbody tr:hover td { background: rgba(139,92,246,0.06) !important; }
 
/* ── Chat input ── */
[data-testid="stChatInput"] { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 16px !important; backdrop-filter: blur(12px) !important; }
[data-testid="stChatInput"]:focus-within { border-color: rgba(139,92,246,0.5) !important; box-shadow: 0 0 0 2px rgba(139,92,246,0.15) !important; }
[data-testid="stChatInput"] textarea { color: #f1f0ff !important; font-family: 'DM Sans', sans-serif !important; background: transparent !important; }
[data-testid="stChatInput"] textarea::placeholder { color: rgba(255,255,255,0.3) !important; }
[data-testid="stChatInput"] button { background: linear-gradient(135deg, #8b5cf6, #22d3ee) !important; border-radius: 50% !important; border: none !important; }
 
hr { border-color: rgba(255,255,255,0.08) !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Auth Config

CONFIG_FILE = "auth_config.yaml"
 
if not os.path.exists(CONFIG_FILE):
    default_config = {
        "credentials": {
            "usernames": {}
        },
        "cookie": {
            "name": "taskbot_pro_cookie",
            "key": "taskbot_super_secret_key_2026",
            "expiry_days": 7
        }
    }
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(default_config, f)
 
with open(CONFIG_FILE) as f:
    config = yaml.load(f, Loader=SafeLoader)
 
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

# Login / Register UI

if not st.session_state.get("authentication_status"):
 
    st.markdown("""
    <div style="
        text-align: center;
        padding: 48px 40px 40px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        backdrop-filter: blur(20px);
        background-image: linear-gradient(135deg, rgba(139,92,246,0.1) 0%, transparent 50%, rgba(34,211,238,0.05) 100%);
        margin-bottom: 36px;
    ">
        <div style="
            display: inline-block; padding: 6px 16px; border-radius: 100px;
            font-size: 11px; letter-spacing: 2px; font-weight: 500; text-transform: uppercase;
            background: rgba(139,92,246,0.2); border: 1px solid rgba(139,92,246,0.4);
            color: #a78bfa; margin-bottom: 20px; font-family: 'DM Sans', sans-serif;
        ">⚡ AI-Powered Task Intelligence</div>
        <h1 style="
            font-family: 'Syne', sans-serif; font-size: 3.4rem; font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #22d3ee 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; letter-spacing: -1px; line-height: 1.1; margin: 0 0 12px 0;
        ">TaskBot Pro</h1>
        <p style="font-size: 0.95rem; color: rgba(255,255,255,0.4); font-family: 'DM Sans', sans-serif; font-weight: 300; margin: 0;">
            The Proactive Neural Bridge for <strong style="color:rgba(255,255,255,0.6)">PostgreSQL</strong> 🧠
        </p>
    </div>
    """, unsafe_allow_html=True)
 
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
 
    with tab1:
        authenticator.login(location="main")
        if st.session_state.get("authentication_status") is False:
            st.error("❌ Incorrect username or password")
 
    with tab2:
        try:
            email, username, name = authenticator.register_user(location="main")
            if email:
                with open(CONFIG_FILE, "w") as f:
                    yaml.dump(config, f)
                st.success(f"✅ Account created! Welcome **{name}** — go to Login tab to sign in.")
        except Exception as e:
            st.error(f"Registration error: {e}")
 
    st.stop()

# Authenticated

username = st.session_state["username"]
name = st.session_state["name"]

# DB Connection

host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
user_db = os.getenv("DB_USER")
password_db = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
 
encoded_user = urllib.parse.quote_plus(user_db)
encoded_password = urllib.parse.quote_plus(password_db)
 
db_uri = f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{host}:{port}/{db_name}?sslmode=require"
db = SQLDatabase.from_uri(db_uri, engine_args={"poolclass": NullPool})
 
db.run("""
    CREATE TABLE IF NOT EXISTS tasks(
        id SERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT CHECK (status IN ('pending','in_progress','completed')) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

# LLM + Agent

model = ChatGroq(model="openai/gpt-oss-20b")
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()
 
system_prompt = f"""
You are **TaskBot Pro**, an intelligent task management assistant connected to a **PostgreSQL database**.
 
The currently logged-in user is: **{username}**
 
CRITICAL RULE: You MUST always filter ALL queries by user_id = '{username}'.
- SELECT queries: always add WHERE user_id = '{username}'
- INSERT queries: always include user_id = '{username}'
- UPDATE/DELETE queries: always add WHERE user_id = '{username}'
- NEVER show tasks from other users under any circumstances
 
---
 
# DATABASE SCHEMA
 
Table: **tasks**
 
Columns:
- id (SERIAL PRIMARY KEY)
- user_id (TEXT, always = '{username}')
- title (TEXT, required)
- description (TEXT)
- status (pending, in_progress, completed)
- created_at (TIMESTAMP)
 
---
 
# OUTPUT FORMAT (MANDATORY)
 
All task results MUST be shown as a **Markdown table**.
 
| ID | Title | Status | Created At |
|----|-------|--------|------------|
 
Status emoji mapping:
pending → 📥 Pending
in_progress → ⏳ In Progress
completed → ✅ Completed
 
- Never return raw SQL results
- Never show SQL queries to the user
 
---
 
# QUERY RULES
 
All SELECT queries MUST include:
WHERE user_id = '{username}'
ORDER BY created_at DESC
LIMIT 10
 
---
 
# TASK IDENTIFICATION
 
If a user refers to a task by title:
1. SELECT to find it (with user_id filter)
2. Get the ID
3. Use ID for update/delete
 
---
 
# TASK OPERATIONS
 
Creating: default status = pending, always set user_id = '{username}'
Updating: identify by ID or title, confirm with SELECT
Deleting: specific WHERE condition including user_id, confirm with SELECT
 
---
 
# SAFETY RULES
 
Never execute: DROP TABLE, TRUNCATE, ALTER TABLE, DELETE without WHERE
Only operate on the tasks table.
 
---
 
# PROACTIVE ASSISTANCE
 
Task not found: "I couldn't find that task. Would you like me to add it?"
Empty search: suggest creating a related task.
 
---
 
# COMMUNICATION STYLE
 
Professional, Clear, Concise, Helpful.
"""
 
@st.cache_resource
def get_agent(_model, _tools, _username):
    agent = create_agent(
        model=_model,
        tools=_tools,
        checkpointer=InMemorySaver(),
        system_prompt=system_prompt
    )
    return agent
 
agent = get_agent(model, tools, username)

# Header

col_title, col_logout = st.columns([5, 1])
 
with col_title:
    st.markdown(f"""
    <div style="
        padding: 36px 40px 32px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        backdrop-filter: blur(20px);
        background-image: linear-gradient(135deg, rgba(139,92,246,0.1) 0%, transparent 50%, rgba(34,211,238,0.05) 100%);
        margin-bottom: 28px;
    ">
        <div style="
            display: inline-block; padding: 6px 16px; border-radius: 100px;
            font-size: 11px; letter-spacing: 2px; font-weight: 500; text-transform: uppercase;
            background: rgba(139,92,246,0.2); border: 1px solid rgba(139,92,246,0.4);
            color: #a78bfa; margin-bottom: 16px; font-family: 'DM Sans', sans-serif;
        ">⚡ AI-Powered Task Intelligence</div>
        <h1 style="
            font-family: 'Syne', sans-serif; font-size: 3rem; font-weight: 800;
            background: linear-gradient(135deg, #fff 0%, #a78bfa 50%, #22d3ee 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; letter-spacing: -1px; line-height: 1.1; margin: 0 0 10px 0;
        ">TaskBot Pro</h1>
        <p style="font-size: 0.9rem; color: rgba(255,255,255,0.4); font-family: 'DM Sans', sans-serif; margin: 0;">
            Welcome back, <strong style="color:#a78bfa">{name}</strong> 👋
        </p>
    </div>
    """, unsafe_allow_html=True)
 
with col_logout:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.session_state.get("authentication_status"):
        authenticator.logout("Logout", location="main")

# Metrics

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("🗄️  ENGINE", "PostgreSQL", "Stable ✓")
with m2:
    st.metric("🧠  INTELLIGENCE", "Groq LLM", "Active")
with m3:
    st.metric("⚡  MODE", "Proactive", "Enabled")
with m4:
    st.metric("👤  USER", username, "Logged In")
 
st.markdown("<br>", unsafe_allow_html=True)
st.info(f"💡 **System Note:** Logged in as **{username}**. Your tasks are private and isolated from other users.")
st.markdown("<br>", unsafe_allow_html=True)

# Chat

chat_key = f"messages_{username}"
if chat_key not in st.session_state:
    st.session_state[chat_key] = []
 
for message in st.session_state[chat_key]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
 
prompt = st.chat_input("Ask me to manage your tasks…")
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state[chat_key].append({"role": "user", "content": prompt})
 
    with st.chat_message("assistant"):
        with st.spinner("Processing…"):
            response = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                {"configurable": {"thread_id": username}}
            )
            result = response["messages"][-1].content
            st.markdown(result)
            st.session_state[chat_key].append({"role": "assistant", "content": result})

