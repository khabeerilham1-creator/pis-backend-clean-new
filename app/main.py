from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# IMPORT ROUTES
from app.routes.patient import router as patient_router
from app.routes.checkup import router as checkup_router

app = FastAPI()

# ✅ CORS (IMPORTANT for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES
app.include_router(patient_router)
app.include_router(checkup_router)

# ROOT TEST
@app.get("/")
def home():
    return {"message": "API running 🚀"}