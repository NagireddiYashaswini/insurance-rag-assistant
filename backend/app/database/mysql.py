import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# ----------------------------
# Load ENV
# ----------------------------

load_dotenv()

# ----------------------------
# Database URL
# ----------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

# ----------------------------
# Engine
# ----------------------------

engine = create_engine(
    DATABASE_URL
)

# ----------------------------
# Session
# ----------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ----------------------------
# Base
# ----------------------------

Base = declarative_base()

# ----------------------------
# Import Models
# ----------------------------

from app.models.user_model import User
from app.models.chat_model import Chat

# ----------------------------
# Create Tables
# ----------------------------

Base.metadata.create_all(
    bind=engine
)

print("Database Connected Successfully")