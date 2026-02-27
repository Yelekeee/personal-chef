import uuid
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str


class ImageUrlRequest(BaseModel):
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_url: str
    question: str = "Please describe this image."


class ChatResponse(BaseModel):
    thread_id: str
    response: str
