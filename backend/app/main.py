
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.routes.history import router as history_router

from app.routes.auth import router as auth_router

from app.routes.upload import router as upload_router

from app.routes.chat import router as chat_router

from app.routes.documents import router as documents_router

# ----------------------------
# FastAPI App
# ----------------------------

app = FastAPI()

# ----------------------------
# CORS
# ----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Routes
# ----------------------------

app.include_router(auth_router)

app.include_router(upload_router)

app.include_router(chat_router)

app.include_router(history_router)

app.include_router(documents_router)

# ----------------------------
# Home Route
# ----------------------------

@app.get("/")
def home():

    return {
        "message": "Insurance RAG Backend Running"
    }

