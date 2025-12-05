from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

class QuestionVersion(Base):
    __tablename__ = "question_versions"

    id = Column(BigInteger, primary_key=True, index=True)
    question_id = Column(
        BigInteger,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    options = Column(JSONB, nullable=False)
    correct_index = Column(Integer, nullable=False)

    question = relationship("Question", back_populates="versions")

    attempts_links = relationship(
        "AttemptQuestion",
        back_populates="question_version",
    )

    answers = relationship(
        "Answer",
        back_populates="question_version",
    )

    __table_args__ = (
        UniqueConstraint("question_id", "version", name="uq_question_version"),
    )