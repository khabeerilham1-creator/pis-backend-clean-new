from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ IMPORT YOUR REAL AUTH ROUTE
from app.routes import auth

app = FastAPI()

# ✅ FIXED CORS (NO "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://clinic-client-lake.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ TEST ROUTE
@app.get("/")
def home():
    return {"message": "API running 🚀"}

# ✅ USE YOUR REAL LOGIN SYSTEM
app.include_router(auth.router)