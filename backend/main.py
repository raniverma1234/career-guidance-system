from fastapi import FastAPI

app = FastAPI(title="AI Career Guidance System")

@app.get("/")
def home():
    return {"message": "Backend is running"}