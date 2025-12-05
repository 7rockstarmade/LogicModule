from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Question(Base):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True, index=True)
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    author = relationship("User", back_populates="questions_authored")

    versions = relationship(
        "QuestionVersion",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionVersion.version",
    )

    tests_links = relationship(
        "TestQuestion",
        back_populates="question",
    )

    attempts_links = relationship(
        "AttemptQuestion",
        back_populates="question",
    )

    answers = relationship(
        "Answer",
        back_populates="question",
    )
