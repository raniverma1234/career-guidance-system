from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import models
import routes_auth
import routes_profile
import routes_assessment
import routes_recommendation
import routes_careers
import routes_roadmap
import routes_resume
import routes_explorer
import routes_progress
import routes_assistant
import routes_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Career Guidance System")

# lets the React frontend (localhost:5173) talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_auth.router)
app.include_router(routes_profile.router)
app.include_router(routes_assessment.router)
app.include_router(routes_recommendation.router)
app.include_router(routes_careers.router)
app.include_router(routes_roadmap.router)
app.include_router(routes_resume.router)  
app.include_router(routes_explorer.router)  
app.include_router(routes_progress.router)
app.include_router(routes_assistant.router)
app.include_router(routes_admin.router)


@app.get("/")
def home():
    return {"message": "Backend is running"}