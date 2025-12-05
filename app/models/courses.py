from sqlalchemy import Boolean, Column, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    teacher_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, nullable=False, default=False)

    teacher = relationship("User", back_populates="courses_taught")

    students_links = relationship(
        "CourseUser",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    tests = relationship(
        "Test",
        back_populates="course",
        cascade="all, delete-orphan",
    )