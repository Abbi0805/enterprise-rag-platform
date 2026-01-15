from fastapi import APIRouter, Depends, HTTPException, Body, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
import time
from src.auth.middleware import get_current_user
from src.auth.models import User
# from src.api.main import orchestrator # Removed to avoid circular import

router = APIRouter()

# --- OpenAI Types ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Dict[str, int]

class ModelCard(BaseModel):
    id: str
    object: str = "model"
    created: int = 1677610602
    owned_by: str = "enterprise-rag"

class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelCard]

# --- Endpoints ---

@router.get("/", response_model=Dict[str, str])
async def root():
    return {"status": "OpenAI Compatible API Ready"}

@router.get("/models", response_model=ModelList)
async def list_models(user: User = Depends(get_current_user)):
    return ModelList(data=[
        ModelCard(id="enterprise-rag-v1"),
        ModelCard(id="gpt-4o"), # Proxy
    ])

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: Request,
    chat_request: ChatCompletionRequest,
    user: User = Depends(get_current_user)
):
    orchestrator = getattr(request.app.state, "orchestrator", None)
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")

    # Extract query from last message
    if not chat_request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    last_message = chat_request.messages[-1]
    if last_message.role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")
    
    query_text = last_message.content

    # Call RAG Orchestrator
    # We ignore streaming for now (Open Web UI handles non-streaming fine usually, though streaming is better UX)
    result = await orchestrator.query(query_text, user)
    answer = result["answer"]

    # Construct Response
    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time())}",
        created=int(time.time()),
        model=chat_request.model,
        choices=[
            ChatChoice(
                index=0,
                message=ChatMessage(role="assistant", content=answer),
                finish_reason="stop"
            )
        ],
        usage={
            "prompt_tokens": 0, # TODO: Get from result if available
            "completion_tokens": 0,
            "total_tokens": 0
        }
    )
