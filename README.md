# RepoMind: AI Debug Copilot

**RepoMind** is a production-ready AI Code Intelligence System that leverages the **Endee Vector Database** to provide semantic search, RAG-based explanation, and automated debugging for codebases.

## Features

- **Semantic Code Search**: Find code by intent, not just keywords.
- **RAG Explainer**: Ask "How does authentication work?" and get an answer grounded in the code.
- **AI Debugger**: Paste a stack trace and get a fix with reasoning.
- **Endee Powered**: Uses high-performance vector search.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Vector DB**: Endee
- **Agents**: LangChain + Ollama (Local LLM)
- **Frontend**: Streamlit
- **Containerization**: Docker

## Setup & Installation

### Prerequisites
1. **Python 3.10+**
2. **Endee Vector DB** running (see [EndeeLabs/endee](https://github.com/EndeeLabs/endee))

### Local Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start RepoMind**
   ```bash
   start_repomind.bat
   ```

### Docker Run

```bash
docker-compose up --build
```

## Usage

1. Open the UI at `http://localhost:8501`.
2. Enter the path to the repository you want to index (e.g., `./` to index RepoMind itself).
3. Click **Index Repository**.
4. Use the sidebar to switch between:
   - **Code Search**: "Find the database wrapper"
   - **Q&A**: "Explain the indexing logic"
   - **Debug Agent**: Paste an error trace.

## Architecture

See [design.md](./design.md) for a detailed architecture breakdown.

## Implementation Details

- **`core/indexer.py`**: Uses Python's `ast` module to parses functions and classes, chunks them, and embeds them using `sentence-transformers`.
- **`core/database.py`**: Wraps the Endee client for vector operations.
- **`agents/debug_agent.py`**: Implements a reasoning loop to analyze error traces against retrieved code context.
