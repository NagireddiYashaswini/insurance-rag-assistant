from fastapi import APIRouter, UploadFile, File
import shutil
import os

from app.services.pdf_service import extract_pages_from_pdf
from app.services.chunk_service import chunk_pages
from app.services.vector_service import store_chunks

router = APIRouter()

UPLOAD_FOLDER = "uploads"

# Create uploads folder automatically
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    try:

        # Save uploaded PDF
        file_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text page-by-page so every chunk can carry an
        # accurate page number through to citations later.
        pages = extract_pages_from_pdf(
            file_path
        )

        # Convert pages into page-aware chunks
        chunks = chunk_pages(
            pages
        )

        print("Total chunks:", len(chunks))
        print(chunks[:2])

        # Store chunks in ChromaDB
        store_chunks(
            chunks,
            file.filename
        )

        print("Stored filename:", file.filename)

        return {
            "message": "File processed successfully",
            "filename": file.filename,
            "total_chunks": len(chunks),
            "total_pages": len(pages),
            "sample_chunk": chunks[0]["text"] if chunks else ""
        }

    except Exception as e:

        return {
            "error": str(e)
        }
