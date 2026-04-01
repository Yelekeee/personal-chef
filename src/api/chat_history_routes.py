from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db import crud
from src.auth.security import decode_access_token
from src.api.history_models import ChatSessionRecord, ChatMessageRecord

chat_history_router = APIRouter(prefix="/chat-sessions", tags=["chat-history"])


def _require_user_id(token: str, db: Session) -> str:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Авторизация қажет.")
    return user_id


class CreateSessionRequest(BaseModel):
    token: str
    title: str = "Жаңа әңгіме"


@chat_history_router.get("", response_model=list[ChatSessionRecord])
def list_sessions(token: str = Query(...), db: Session = Depends(get_db)):
    user_id = _require_user_id(token, db)
    sessions = crud.get_chat_sessions_for_user(db, user_id)
    return [ChatSessionRecord.model_validate(s) for s in sessions]


@chat_history_router.post("", response_model=ChatSessionRecord)
def create_session(body: CreateSessionRequest, db: Session = Depends(get_db)):
    user_id = _require_user_id(body.token, db)
    session = crud.create_chat_session(db, user_id, body.title)
    return ChatSessionRecord.model_validate(session)


@chat_history_router.get("/{session_id}/messages", response_model=list[ChatMessageRecord])
def get_messages(session_id: str, token: str = Query(...), db: Session = Depends(get_db)):
    user_id = _require_user_id(token, db)
    session = crud.get_chat_session(db, session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сессия табылмады.")
    messages = crud.get_messages_for_session(db, session_id)
    return [ChatMessageRecord.model_validate(m) for m in messages]


@chat_history_router.delete("/{session_id}")
def delete_session(session_id: str, token: str = Query(...), db: Session = Depends(get_db)):
    user_id = _require_user_id(token, db)
    session = crud.get_chat_session(db, session_id, user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сессия табылмады.")
    crud.delete_chat_session(db, session)
    return {"message": "Сессия жойылды."}
