from fastapi import APIRouter
from fastapi import Header
from pydantic import BaseModel
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.mysql import SessionLocal

from app.models.chat_model import Chat

from app.auth.jwt_handler import (
    decode_access_token
)

from app.services.vector_service import (
    search_chunks
)

from app.services.llm_service import (
    generate_answer,
    NO_CONTEXT_MESSAGE
)

router = APIRouter()


class HistoryTurn(BaseModel):
    question: str
    answer: str


class AskRequest(BaseModel):
    query: str
    filename: str

    # Previous chat history
    history: Optional[List[HistoryTurn]] = None


@router.post("/ask")
def ask_question(
    body: AskRequest,
    authorization: str = Header(None)
):

    try:

        # ----------------------------
        # Check Authorization
        # ----------------------------

        if not authorization:

            return {
                "error": "Authorization token missing"
            }

        # ----------------------------
        # Decode JWT
        # ----------------------------

        token = authorization.split(" ")[1]

        payload = decode_access_token(token)

        user_email = payload["email"]

        query = body.query
        filename = body.filename

        history = (
            [turn.dict() for turn in body.history]
            if body.history
            else None
        )

        # ----------------------------
        # Search Chunks
        # ----------------------------

        results = search_chunks(
            query,
            filename
        )

        documents = list(results["documents"])
        metadatas = list(results["metadatas"])

        context_chunks = []

        for i in range(len(documents)):

            doc = documents[i]

            # If document is dict
            if isinstance(doc, dict):

                text = doc.get("text", "")

            else:

                text = str(doc)

            page = None

            if i < len(metadatas) and metadatas[i]:

                page = metadatas[i].get("page")

            context_chunks.append({

                "text": text,

                "page": page
            })

        # ----------------------------
        # No Context Found
        # ----------------------------

        if not context_chunks:

            print(
                "No matching chunks found for filename:",
                filename
            )

            answer = NO_CONTEXT_MESSAGE

            sources = []

        else:

            # ----------------------------
            # Generate Answer
            # ----------------------------

            result = generate_answer(
                question=query,
                context_chunks=context_chunks,
                history=history
            )

            answer = result["answer"]

            sources = result["sources"]

            # Fallback sources
            if not sources and answer != NO_CONTEXT_MESSAGE:

                sources = context_chunks

        # ----------------------------
        # Save Chat
        # ----------------------------

        db: Session = SessionLocal()

        new_chat = Chat(
            user_email=user_email,
            question=query,
            answer=answer,
            filename=filename
        )

        db.add(new_chat)

        db.commit()

        db.close()

        # ----------------------------
        # Return Response
        # ----------------------------

        return {

            "question": query,

            "answer": answer,

            "sources": sources
        }

    except Exception as e:

        print("ERROR:", str(e))

        return {
            "error": str(e)
        }
