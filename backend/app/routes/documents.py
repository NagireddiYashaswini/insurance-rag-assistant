from fastapi import APIRouter, Header
import os

from app.auth.jwt_handler import decode_access_token
from app.services.vector_service import list_documents, delete_document

router = APIRouter()

UPLOAD_FOLDER = "uploads"


@router.get("/documents")
def get_documents(authorization: str = Header(None)):
    """
    Lists every PDF currently indexed in the vector store, so the
    frontend can offer a document switcher instead of only remembering
    the single most-recently-uploaded filename in localStorage.
    """

    if not authorization:
        return {"error": "Authorization token missing"}

    try:
        token = authorization.split(" ")[1]
        decode_access_token(token)
    except Exception:
        return {"error": "Invalid or expired token"}

    try:
        filenames = list_documents()

        documents = []

        for filename in filenames:

            file_path = os.path.join(UPLOAD_FOLDER, filename)

            size_bytes = (
                os.path.getsize(file_path)
                if os.path.exists(file_path)
                else None
            )

            documents.append({
                "filename": filename,
                "size_bytes": size_bytes
            })

        return {"documents": documents}

    except Exception as e:
        return {"error": str(e)}


@router.delete("/documents/{filename}")
def remove_document(filename: str, authorization: str = Header(None)):
    """
    Removes a document's chunks from the vector store and its file
    from disk. This is what lets a user clean up documents they no
    longer need instead of the index growing forever.
    """

    if not authorization:
        return {"error": "Authorization token missing"}

    try:
        token = authorization.split(" ")[1]
        decode_access_token(token)
    except Exception:
        return {"error": "Invalid or expired token"}

    try:
        deleted_chunks = delete_document(filename)

        file_path = os.path.join(UPLOAD_FOLDER, filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "message": "Document deleted",
            "filename": filename,
            "deleted_chunks": deleted_chunks
        }

    except Exception as e:
        return {"error": str(e)}
