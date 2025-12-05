from fastapi import FastAPI
from app.core.config import settings
from app.models import *

app = FastAPI(title=settings.app_name)