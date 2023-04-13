from fastapi import FastAPI
from .routers import user
from .database import SessionLocal, db_engine, Base
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=db_engine)

app = FastAPI()

origins = ["http://localhost:3000", "https://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, tags=["auth"])
