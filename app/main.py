from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTES
from app.routes.patient import router as patient_router
from app.routes.checkup import router as checkup_router

app = FastAPI()

# ✅ FIX CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://clinic-client-six.vercel.app"  # 🔥 YOUR FRONTEND
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(patient_router)
app.include_router(checkup_router)

@app.get("/")
def home():
    return {"message": "API running 🚀"}