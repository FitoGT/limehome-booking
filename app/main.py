from fastapi import FastAPI
from app.db.init_db import init_db
from app.db.database import get_db
from app.controllers.booking_controller import router as booking_router

init_db()

app = FastAPI()

app.include_router(booking_router)
