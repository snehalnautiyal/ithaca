from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.auth import router as auth_router
from core.config import settings
from core.database import SessionLocal, create_tables
from core.auth import ensure_admin
from core.middleware import AuthMiddleware
from routes.session import router as session_router
from routes.chat import router as chat_router
from routes.model import router as model_router
from routes.memory import router as memory_router
from routes.document import router as document_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    db = SessionLocal()
    try:
        ensure_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Ithaca", lifespan=lifespan)
app.add_middleware(AuthMiddleware)
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(chat_router)
app.include_router(model_router)
app.include_router(memory_router)
app.include_router(document_router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.get("/")
async def index():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")


if __name__ == "__main__":
    uvicorn.run("app:app", host=settings.app_bind, port=settings.app_port, reload=True)
