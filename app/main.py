from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS (FINAL WORKING CONFIG)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (for now)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ TEST ROUTE
@app.get("/")
def home():
    return {"message": "API running 🚀"}

# ✅ IMPORTANT: HANDLE PREFLIGHT (CORS FIX)
@app.options("/auth/login")
def options_login():
    return {"ok": True}

# ✅ LOGIN ROUTE
@app.post("/auth/login")
def login(data: dict):
    if data.get("username") == "admin@hdc.com" and data.get("password") == "123456":
        return {"access_token": "dummy_token"}
    return {"error": "Invalid credentials"}