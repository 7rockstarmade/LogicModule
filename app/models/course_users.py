from app.db.base import Base
from datetime import datetime
from sqlalchemy import Column, BigInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship

class CourseUser(Base):
    __tablename__ = "course_users"

    course_id = Column(
        BigInteger,
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    enrolled_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    course = relationship("Course", back_populates="students_links")
    user = relationship("User", back_populates="course_links")