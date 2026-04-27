from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS FIX (FINAL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clinic-client-lake.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 IMPORTANT: import routes AFTER CORS
from app.routes import auth  # adjust if different

app.include_router(auth.router)

@app.get("/")
def home():
    return {"message": "API running 🚀"}