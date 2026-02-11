import streamlit as st
import requests
import json

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="RepoMind",
    page_icon="jg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #fca311; /* Vibrant Orange */
        font-family: 'Helvetica Neue', sans-serif;
    }
    h2, h3 {
        color: #e5e5e5;
    }
    .stButton>button {
        background-color: #fca311;
        color: #000000;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #fb8500;
        color: #ffffff;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    /* Card style for results */
    .result-card {
        background-color: #1a1e24;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/stencil/96/fca311/brain.png", width=64)
    st.title("RepoMind")
    st.markdown("*AI Code Intelligence*")
    
    st.markdown("---")
    st.header("⚙️ Configuration")
    
    repo_path = st.text_input("Repository Path", value="./", help="Absolute path to the codebase you want to analyze.")
    
    if st.button("🚀 Index Repository"):
        with st.spinner("🧠 Reading and understanding code..."):
            try:
                res = requests.post(f"{API_URL}/index", json={"repo_path": repo_path})
                if res.status_code == 200:
                    st.success("Indexing started successfully! Check console for progress.")
                else:
                    st.error(f"Failed to start indexing: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    st.markdown("---")
    mode = st.radio("Choose Mode", ["🔍 Code Search", "🤔 Q&A Explainer", "🐞 Debug Agent"])
    
    st.markdown("---")
    st.markdown("FAILED? Check if `Ollama` is running for AI features.")

# Main Area
if mode == "🔍 Code Search":
    st.title("Semantic Code Search")
    st.markdown("Find functionality by *intent*, not just keywords.")
    
    query = st.text_input("Search Query", "authentication middleware", placeholder="e.g., 'how is the database connection handled?'")
    
    if st.button("Search Code"):
        with st.spinner("Searching vector database..."):
            try:
                res = requests.post(f"{API_URL}/search", json={"query": query})
                
                # Robust Error Handling
                if res.status_code != 200:
                    st.error(f"API Error ({res.status_code}): {res.text}")
                else:
                    try:
                        results = res.json().get("results", [])
                        if not results:
                            st.warning("No results found.")
                        
                        for idx, r in enumerate(results):
                            with st.expander(f"📄 {r.get('name')} ({r.get('file_path')})", expanded=(idx==0)):
                                st.markdown(f"**Relevance Score:** {r.get('score', 'N/A')}")
                                st.code(r.get('content'), language=r.get('language', 'python'))
                    except json.JSONDecodeError:
                        st.error("Error: API returned invalid JSON. " + res.text)
                        
            except Exception as e:
                st.error(f"Connection Error: {e}")

elif mode == "🤔 Q&A Explainer":
    st.title("Codebase Q&A")
    st.markdown("Ask high-level questions about the architecture or logic.")
    
    question = st.text_area("Your Question", "How is the database connection handled?", height=100)
    
    if st.button("Ask AI"):
        with st.spinner("Analyzing code context and generating answer..."):
            try:
                res = requests.post(f"{API_URL}/explain", json={"question": question})
                
                if res.status_code != 200:
                     st.error(f"API Error ({res.status_code}): {res.text}")
                else:
                    try:
                        answer = res.json().get("answer", "")
                        st.markdown("### Answer")
                        st.info(answer)
                    except json.JSONDecodeError:
                         st.error("Error: API returned invalid JSON. " + res.text)
            except Exception as e:
                st.error(f"Error: {e}")

elif mode == "🐞 Debug Agent":
    st.title("AI Debugger")
    st.markdown("Paste a stack trace to get a fix grounded in your actual code.")
    
    error_trace = st.text_area("Paste Stack Trace", height=200, placeholder="Traceback (most recent call last)...")
    
    if st.button("Analyze & Fix"):
        with st.spinner("Debugging..."):
            try:
                res = requests.post(f"{API_URL}/debug", json={"error_trace": error_trace})
                
                if res.status_code != 200:
                     st.error(f"API Error ({res.status_code}): {res.text}")
                else:
                    try:
                        analysis = res.json().get("analysis", "")
                        st.markdown("### Diagnosis & Fix")
                        st.markdown(analysis)
                    except json.JSONDecodeError:
                         st.error("Error: API returned invalid JSON. " + res.text)
            except Exception as e:
                st.error(f"Error: {e}")
