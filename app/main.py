from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔥 FIXED IMPORT (matches your file name)
from app.routes.patient import router as patients_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API running 🚀"}


@app.post("/auth/login")
def login(data: dict):
    if data.get("username") == "admin@hdc.com" and data.get("password") == "123456":
        return {"access_token": "dummy_token"}
    return {"error": "Invalid"}


# 🔥 CONNECT ROUTER
app.include_router(patients_router)