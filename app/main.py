from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS (WORKING CONFIG)
origins = [
    "https://clinic-client-lake.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 TEST ROUTE
@app.get("/")
def home():
    return {"message": "API running 🚀"}

# 🔥 LOGIN ROUTE (TEMP SIMPLE)
@app.post("/auth/login")
def login(data: dict):
    if data.get("username") == "admin@hdc.com" and data.get("password") == "123456":
        return {"access_token": "dummy_token"}
    return {"error": "Invalid"}