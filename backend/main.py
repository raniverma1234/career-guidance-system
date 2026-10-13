from fastapi import FastAPI
from database import engine, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Career Guidance System")


@app.get("/")
def home():
    return {"message": "Backend is running"}