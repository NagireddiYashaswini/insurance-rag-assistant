
from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# ----------------------------
# Database URL
# ----------------------------

DATABASE_URL = "mysql+pymysql://root:root123@localhost/insurance_rag"

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
# IMPORTANT:
# Import AFTER Base creation
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

