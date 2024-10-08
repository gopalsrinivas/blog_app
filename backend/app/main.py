from fastapi.staticfiles import StaticFiles
from app.core.config import settings, MEDIA_DIR
import os
import logging
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy import text
from app.routers.categories import router
from app.models.categories import *
from app.core.logging import logging
from app.routers import categories, subcategories, blog
from app.utils.send_notifications.send_notifications import router as notification_router


app = FastAPI(title="FastAPI Blog Application", docs_url="/api_v1/docs", redoc_url="/api_v1/redoc")

# Mount media files directory
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(subcategories.router, prefix="/api/subcategories", tags=["Subcategories"])
app.include_router(blog.router, prefix="/api/blog", tags=["blog"])
app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])



@app.on_event("startup")
async def startup_event():
    logging.info("Application startup application...")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down application...")
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.get("/health")
async def health_check():
    return {"status": "ok"}


