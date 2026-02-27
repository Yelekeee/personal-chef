import uuid
import tempfile
import os
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from langchain_core.messages import HumanMessage

from src.api.models import ChatRequest, ImageUrlRequest, ChatResponse
from src.utils.multimodal import create_image_url_message, create_image_file_message

router = APIRouter()


def _extract_response(result: dict) -> str:
    """Pull the last AIMessage text out of a graph result."""
    for msg in reversed(result.get("messages", [])):
        if msg.__class__.__name__ == "AIMessage":
            content = msg.content
            if isinstance(content, list):
                return "\n".join(
                    c.get("text", "") for c in content
                    if isinstance(c, dict) and c.get("type") == "text"
                )
            return str(content)
    return ""


async def _run(graph, message, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = await graph.ainvoke({"messages": [message]}, config=config)
    return _extract_response(result)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest):
    graph = request.app.state.graph
    try:
        response = await _run(graph, HumanMessage(content=body.message), body.thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ChatResponse(thread_id=body.thread_id, response=response)


@router.post("/chat/image-url", response_model=ChatResponse)
async def chat_image_url(request: Request, body: ImageUrlRequest):
    graph = request.app.state.graph
    try:
        msg = create_image_url_message(body.question, body.image_url)
        response = await _run(graph, msg, body.thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ChatResponse(thread_id=body.thread_id, response=response)


@router.post("/chat/image-file", response_model=ChatResponse)
async def chat_image_file(
    request: Request,
    file: UploadFile = File(...),
    question: str = Form(default="Please describe this image."),
    thread_id: str = Form(default=None),
):
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    graph = request.app.state.graph
    suffix = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        msg = create_image_file_message(question, tmp_path)
        response = await _run(graph, msg, thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return ChatResponse(thread_id=thread_id, response=response)


@router.delete("/chat/{thread_id}")
async def clear_thread(thread_id: str):
    """Signal to the client to stop using this thread_id.

    MemorySaver state is in-process memory. Simply generate a new thread_id
    on the client side to start a fresh conversation.
    """
    return {"message": f"Conversation {thread_id} cleared. Use a new thread_id to start fresh."}
