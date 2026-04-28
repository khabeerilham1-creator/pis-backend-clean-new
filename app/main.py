from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ IMPORT ROUTER
from app.routes.patients import router as patients_router

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CONNECT ROUTES
app.include_router(patients_router, prefix="/api")

# ✅ ROOT
@app.get("/")
def home():
    return {"message": "API running 🚀"}

# ✅ LOGIN
@app.post("/auth/login")
def login(data: dict):
    if data.get("username") == "admin@hdc.com" and data.get("password") == "123456":
        return {"access_token": "dummy_token"}
    return {"error": "Invalid"}