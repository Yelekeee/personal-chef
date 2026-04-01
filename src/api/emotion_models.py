from typing import Literal
from pydantic import BaseModel


EmotionCategory = Literal["happy", "neutral", "stressed", "sad", "anxious"]
EmotionLevel = Literal["low", "medium", "high"]


class TextEmotionRequest(BaseModel):
    text: str  # max 2000 chars
    token: str | None = None


class EmotionResult(BaseModel):
    emotion: EmotionCategory
    level: EmotionLevel
    confidence: float          # 0.0 – 1.0
    analysis: str              # 1-2 sentence explanation
    recommendations: list[str] # 3-5 actionable items
    mental_health_note: str | None = None  # only for stressed/anxious + high


class EmotionResponse(BaseModel):
    scan_method: Literal["face", "text"]
    result: EmotionResult
