from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

class Answer(Base):
    __tablename__ = "answers"

    id = Column(BigInteger, primary_key=True, index=True)
    attempt_id = Column(
        BigInteger,
        ForeignKey("attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(
        BigInteger,
        ForeignKey("questions.id"),
        nullable=False,
    )
    question_version_id = Column(
        BigInteger,
        ForeignKey("question_versions.id"),
        nullable=False,
    )
    value = Column(Integer, nullable=False, default=-1)  # -1 = не отвечено

    attempt = relationship("Attempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    question_version = relationship("QuestionVersion", back_populates="answers")

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "question_id",
            "question_version_id",
            name="uq_answers_attempt_question",
        ),
    )