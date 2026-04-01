from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db import crud
from src.auth.security import decode_access_token
from src.api.history_models import EmotionScanRecord

history_router = APIRouter(prefix="/history", tags=["history"])


def _require_user_id(token: str, db: Session) -> str:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Авторизация қажет.")
    return user_id


@history_router.get("/scans", response_model=list[EmotionScanRecord])
def get_scans(token: str = Query(...), db: Session = Depends(get_db)):
    user_id = _require_user_id(token, db)
    scans = crud.get_scans_for_user(db, user_id)
    return [EmotionScanRecord.model_validate(s) for s in scans]


@history_router.delete("/scans")
def delete_scans(token: str = Query(...), db: Session = Depends(get_db)):
    user_id = _require_user_id(token, db)
    crud.delete_scans_for_user(db, user_id)
    return {"message": "Барлық сканерлеулер жойылды."}
