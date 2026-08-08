from fastapi import FastAPI
from app.api.files import router as files_router
from contextlib import asynccontextmanager
from app.db import create_db_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield

app = FastAPI(lifespan=lifespan)

# tells the app to serve whatever endpoints are there in files.py
# at /files/<endpoint>
app.include_router(files_router, prefix="/files")

@app.get("/health")
async def health():
    return { "status" : "ok" }