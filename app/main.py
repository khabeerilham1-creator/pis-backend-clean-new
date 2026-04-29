from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.routes.patients import router as patients_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES
app.include_router(patients_router, prefix="/api")

# 🔥 SERVE IMAGES
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def home():
    return {"message": "API running 🚀"}


# 🔥 LOGIN FIXED
class LoginData(BaseModel):
    username: str
    password: str

@app.post("/auth/login")
def login(data: LoginData):
    if data.username == "admin@hdc.com" and data.password == "123456":
        return {"access_token": "dummy_token"}
    return {"error": "Invalid"}