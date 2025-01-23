from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan: Starting up...")
    yield
    print("Lifespan: Shutting down...")


app = FastAPI(
    title="FastAPI Project",
    description="A FastAPI project with PostgreSQL and Alembic integration.",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api")
