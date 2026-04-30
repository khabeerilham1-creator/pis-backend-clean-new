from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTES
from app.routes.patient import router as patient_router
from app.routes.checkup import router as checkup_router  # ✅ THIS IS WHAT YOU WERE MISSING

app = FastAPI()

# CORS (IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES REGISTER
app.include_router(patient_router)
app.include_router(checkup_router)  # ✅ THIS FIXES YOUR 404

# TEST ROUTE
@app.get("/")
def home():
    return {"message": "API running 🚀"}