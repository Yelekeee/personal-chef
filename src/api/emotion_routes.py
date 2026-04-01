import os
import tempfile
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from src.api.emotion_models import TextEmotionRequest, EmotionResponse
from src.agent.emotion_analyzer import analyze_face, analyze_text
from src.db.database import get_db
from src.db import crud
from src.auth.security import decode_access_token

emotion_router = APIRouter(prefix="/emotion", tags=["emotion"])


def _maybe_persist_scan(db: Session, token: str | None, scan_method: str, response: EmotionResponse):
    if not token:
        return
    user_id = decode_access_token(token)
    if not user_id:
        return
    r = response.result
    crud.save_emotion_scan(
        db,
        user_id=user_id,
        scan_method=scan_method,
        emotion=r.emotion,
        level=r.level,
        confidence=r.confidence,
        analysis=r.analysis,
        recommendations=list(r.recommendations),
        mental_health_note=r.mental_health_note,
    )


@emotion_router.post("/scan/face", response_model=EmotionResponse)
async def scan_face(
    file: UploadFile = File(...),
    token: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    suffix = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = await analyze_face(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    response = EmotionResponse(scan_method="face", result=result)
    _maybe_persist_scan(db, token, "face", response)
    return response


@emotion_router.post("/scan/text", response_model=EmotionResponse)
async def scan_text(body: TextEmotionRequest, db: Session = Depends(get_db)):
    try:
        result = await analyze_text(body.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    response = EmotionResponse(scan_method="text", result=result)
    _maybe_persist_scan(db, body.token, "text", response)
    return response
