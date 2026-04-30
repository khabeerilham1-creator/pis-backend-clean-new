from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.patient import router as patient_router
from app.routes.checkup import router as checkup_router

app = FastAPI()

# ✅ CORS MUST BE FIRST (before routes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 🔥 use * for now (fix everything instantly)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROUTES AFTER CORS
app.include_router(patient_router)
app.include_router(checkup_router)

@app.get("/")
def home():
    return {"message": "API running"}