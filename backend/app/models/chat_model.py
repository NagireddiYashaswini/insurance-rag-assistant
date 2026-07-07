
from sqlalchemy import Column, Integer, String, Text

from app.database.mysql import Base


class Chat(Base):

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)

    user_email = Column(String(255))

    question = Column(Text)

    answer = Column(Text)

    filename = Column(String(255))

