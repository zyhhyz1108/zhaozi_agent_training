from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.models import Course
from app.routes import router as courses_router
from app.rag.routes import router as knowledge_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="培训课程管理",
    lifespan=lifespan,
)
app.include_router(courses_router)
app.include_router(knowledge_router)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}