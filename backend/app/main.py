from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import create_db_and_tables
from .api import api_router
from .scheduler import start_scheduler, scrape_all_wards
from .seed import seed_wards


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時
    create_db_and_tables()
    seed_wards()
    start_scheduler()
    # 初回スクレイピングを即時実行
    await scrape_all_wards()
    yield
    # 終了時（特に処理なし）


app = FastAPI(
    title="東京23区 区立住宅情報 API",
    description="東京23区の区立住宅最新情報を提供するAPIサービス",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
