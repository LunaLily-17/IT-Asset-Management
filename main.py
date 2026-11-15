from contextlib import asynccontextmanager
from fastapi import FastAPI

from database.db_json import load_db
from routes.asset import router as asset_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_db()
    yield


app = FastAPI(
    title="IT Asset Management API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(asset_router)
