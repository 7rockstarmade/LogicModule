from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, String, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    test_id = Column(BigInteger, ForeignKey("tests.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    score = Column(Numeric, nullable=True)

    user = relationship("User", back_populates="attempts")
    test = relationship("Test", back_populates="attempts")

    questions_links = relationship(
        "AttemptQuestion",
        back_populates="attempt",
        cascade="all, delete-orphan",
        order_by="AttemptQuestion.position",
    )

    answers = relationship(
        "Answer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )