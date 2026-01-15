from fastapi import FastAPI, Depends, HTTPException, Body
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from src.config import settings
from src.auth.middleware import get_current_user
from src.auth.models import User
from src.orchestration.rag import RAGOrchestrator
from src.ingestion.loaders import get_loader_for_file
from src.ingestion.chunking import RecursiveTokenChunker
from src.ingestion.embeddings import EmbeddingGenerator
from src.retrieval.vector import VectorStore
# from src.retrieval.keyword import KeywordSearch # Re-initialize/Load index in prod

# Global Orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting Enterprise RAG Platform...")
    global orchestrator
    orchestrator = RAGOrchestrator()
    app.state.orchestrator = orchestrator
    print("Orchestrator initialized.")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Enterprise RAG Platform",
    description="Enterprise-grade RAG system with evaluation and cost control.",
    version="0.1.0",
    lifespan=lifespan
)

from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def debug_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )

@app.get("/")
async def root():
    return {"message": "Welcome to the Enterprise RAG Platform API. Visit /docs for documentation."}

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

# Include OpenAI Router
from src.api.openai import router as openai_router
app.include_router(openai_router, prefix="/v1")

@app.post("/query")
async def query_endpoint(
    query: str = Body(..., embed=True), 
    user: User = Depends(get_current_user)
):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return await orchestrator.query(query, user)

# Quick ingest endpoint for demo purposes (usually would be async worker)
@app.post("/ingest/demo")
async def ingest_demo_file(
    file_path: str = Body(..., embed=True),
    user: User = Depends(get_current_user)
):
    if "admin" not in user.groups:
        raise HTTPException(status_code=403, detail="Only admins can ingest")
        
    try:
        # Load
        loader = get_loader_for_file(file_path)
        docs = loader.load(file_path)
        
        # Chunk
        chunker = RecursiveTokenChunker()
        all_chunks = []
        for doc in docs:
            # Add access group to metadata for demo
            doc.metadata["access_group"] = "management" if "strategy" in file_path.lower() else "engineering"
            chunks = chunker.chunk(doc)
            all_chunks.extend(chunks)
            
        # Ingest (Embed + Index)
        await orchestrator.retriever.ingest(all_chunks)
        
        return {"status": "success", "chunks_ingested": len(all_chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest/github")
async def ingest_github(
    repo_url: str = Body(..., embed=True),
    user: User = Depends(get_current_user)
):
    if "admin" not in user.groups:
        raise HTTPException(status_code=403, detail="Only admins can ingest")
        
    try:
        from src.ingestion.github import GitHubIngestor
        from src.ingestion.chunking import RecursiveTokenChunker
        
        # Load
        ingestor = GitHubIngestor(repo_url)
        docs = ingestor.ingest()
        
        if not docs:
            return {"status": "warning", "message": "No documents found in repo"}

        # Chunk
        chunker = RecursiveTokenChunker()
        all_chunks = []
        for doc in docs:
            doc.metadata["access_group"] = "public" # GitHub is public usually
            chunks = chunker.chunk(doc)
            all_chunks.extend(chunks)
            
        # Ingest
        if all_chunks:
            await orchestrator.retriever.ingest(all_chunks)
        
        return {"status": "success", "files_processed": len(docs), "chunks_ingested": len(all_chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
