from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship


class TestQuestion(Base):
    
    __tablename__ = "test_questions"

    test_id = Column(
        BigInteger,
        ForeignKey("tests.id", ondelete="CASCADE"),
        primary_key=True,
    )
    question_id = Column(
        BigInteger,
        ForeignKey("questions.id"),
        primary_key=True,
    )
    position = Column(Integer, nullable=False)

    test = relationship("Test", back_populates="questions_links")
    question = relationship("Question", back_populates="tests_links")

    __table_args__ = (
        Index("uq_test_questions_position", "test_id", "position", unique=True),
    )