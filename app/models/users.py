from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    username = Column(String, nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    is_blocked = Column(Boolean, nullable=False, default=False)

    courses_taught = relationship(
        "Course",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )

    course_links = relationship(
        "CourseUser",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    attempts = relationship(
        "Attempt",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    questions_authored = relationship(
        "Question",
        back_populates="author",
    )

    notifications = relationship(
        "Notification", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )