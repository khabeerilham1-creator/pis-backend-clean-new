from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ Proper CORS (don’t mix with custom middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://clinic-client-lake.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
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