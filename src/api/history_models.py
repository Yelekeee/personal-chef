import json
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator


class EmotionScanRecord(BaseModel):
    id: str
    scan_method: str
    emotion: str
    level: str
    confidence: float
    analysis: str
    recommendations: list[str]
    mental_health_note: str | None
    scanned_at: datetime

    @field_validator("recommendations", mode="before")
    @classmethod
    def parse_recommendations(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator("scanned_at", mode="before")
    @classmethod
    def ensure_utc(cls, v):
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    model_config = {"from_attributes": True}


class ChatSessionRecord(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageRecord(BaseModel):
    id: str
    role: str
    content: str
    sent_at: datetime

    model_config = {"from_attributes": True}
