from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.history import router as history_router
from app.routes.auth import router as auth_router
from app.routes.upload import router as upload_router
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router

app = FastAPI()

# Allowed frontend origins
origins = [
    "http://localhost:5173",
    "https://insurance-rag-assistant.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(history_router)
app.include_router(documents_router)

@app.get("/")
def home():
    return {"message": "Insurance RAG Backend Running"}