from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import os

from core.indexer import indexer
from core.retriever import retriever
from agents.qa_agent import qa_agent
from agents.debug_agent import debug_agent
from core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# Request Models
class IndexRequest(BaseModel):
    repo_path: str

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class ExplainRequest(BaseModel):
    question: str
    file_context: Optional[str] = None

class DebugRequest(BaseModel):
    error_trace: str
    context: Optional[str] = None

@app.get("/")
async def root():
    return {"status": "ok", "service": "RepoMind API"}

@app.post("/index")
async def trigger_indexing(request: IndexRequest, background_tasks: BackgroundTasks):
    if not os.path.exists(request.repo_path):
        raise HTTPException(status_code=400, detail="Repository path does not exist")
    
    background_tasks.add_task(indexer.index_repository, request.repo_path)
    return {"status": "accepted", "message": "Indexing started in background"}

@app.post("/search")
async def search_code(request: SearchRequest):
    results = retriever.search(request.query, top_k=request.limit)
    return {"results": results}

@app.post("/explain")
async def explain_code(request: ExplainRequest):
    answer = qa_agent.ask(request.question)
    return {"answer": answer}

@app.post("/debug")
async def debug_error(request: DebugRequest):
    analysis = debug_agent.analyze_error(request.error_trace)
    return {"analysis": analysis}
