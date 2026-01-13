from fastapi import FastAPI
from app.api.routers import users, courses, tests, questions
from app.core.config import settings
from app import models

app = FastAPI(title=settings.app_name)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(tests.router)
app.include_router(questions.router)