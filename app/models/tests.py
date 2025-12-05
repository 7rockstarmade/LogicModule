from app.db.base import Base
from sqlalchemy import Column, BigInteger, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

class Test(Base):
    __tablename__ = "tests"

    id = Column(BigInteger, primary_key=True, index=True)
    course_id = Column(
        BigInteger,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    course = relationship("Course", back_populates="tests")

    questions_links = relationship(
        "TestQuestion",
        back_populates="test",
        cascade="all, delete-orphan",
        order_by="TestQuestion.position",
    )

    attempts = relationship(
        "Attempt",
        back_populates="test",
        cascade="all, delete-orphan",
    )