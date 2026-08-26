from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.files import router as files_router
from app.db import create_db_tables
from app.services.cleanup import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# tells the app to serve whatever endpoints are there in files.py
# at /<endpoint>

@app.get("/health")
async def health():
    return { "status" : "ok" }

app.include_router(files_router)
app.include_router(auth_router)