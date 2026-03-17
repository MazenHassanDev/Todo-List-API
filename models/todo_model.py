from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String(200), nullable=False)
    description:Mapped[str] = mapped_column(Text, nullable=True)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    user:Mapped["User"] = relationship("User", back_populates="todos")