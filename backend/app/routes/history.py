from fastapi import APIRouter, Header

from sqlalchemy.orm import Session

from app.database.mysql import SessionLocal

from app.models.chat_model import Chat

from app.auth.jwt_handler import (
    decode_access_token
)

router = APIRouter()


@router.get("/history")
def get_history(authorization: str = Header(None)):

    token = authorization.split(" ")[1]

    payload = decode_access_token(token)

    user_email = payload["email"]

    db: Session = SessionLocal()

    chats = db.query(Chat).filter(
        Chat.user_email == user_email
    ).all()

    history = []

    for chat in chats:

        history.append({

            "question": chat.question,

            "answer": chat.answer,

            "filename": chat.filename
        })

    db.close()

    return {
        "history": history
    }