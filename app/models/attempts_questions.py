from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey, Integer
from sqlalchemy.orm import relationship

class AttemptQuestion(Base):

    __tablename__ = "attempt_questions"

    attempt_id = Column(
        BigInteger,
        ForeignKey("attempts.id", ondelete="CASCADE"),
        primary_key=True,
    )
    question_id = Column(
        BigInteger,
        ForeignKey("questions.id"),
        primary_key=True,
    )
    question_version_id = Column(
        BigInteger,
        ForeignKey("question_versions.id"),
        primary_key=True,
    )
    position = Column(Integer, nullable=False)

    attempt = relationship("Attempt", back_populates="questions_links")
    question = relationship("Question", back_populates="attempts_links")
    question_version = relationship("QuestionVersion", back_populates="attempts_links")