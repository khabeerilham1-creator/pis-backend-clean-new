from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔥 IMPORT (IMPORTANT — matches your file name: patient.py)
from app.routes.patient import router as patients_router

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ HOME
@app.get("/")
def home():
    return {"message": "API running 🚀"}


# ✅ LOGIN
@app.post("/auth/login")
def login(data: dict):
    if data.get("username") == "admin@hdc.com" and data.get("password") == "123456":
        return {"access_token": "dummy_token"}
    return {"error": "Invalid"}


# 🔥 CONNECT PATIENT ROUTES
app.include_router(patients_router)