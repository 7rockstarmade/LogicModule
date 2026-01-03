from fastapi import FastAPI
from app.api.routers import users, courses
from app.core.config import settings
from app import models

app = FastAPI(title=settings.app_name)
app.include_router(users.router)
app.include_router(courses.router)