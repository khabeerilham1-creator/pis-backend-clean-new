from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# =========================
# IMPORT ROUTES (match your filenames)
# =========================
from app.routes.patient import router as patients_router
from app.routes.checkup import router as checkups_router
from app.routes.afi import router as afi_router
from app.routes.fis import router as fis_router
from app.routes.cis import router as cis_router
from app.routes.timeline import router as timeline_router
from app.routes.auth import router as auth_router
from app.routes.report import router as report_router

# =========================
# INIT APP
# =========================
app = FastAPI(title="Clinic Management API")

# =========================
# CORS (frontend access)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# STATIC FILES (uploads)
# =========================
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# =========================
# ROUTES
# =========================

# Core modules
app.include_router(patients_router, prefix="/patients", tags=["Patients"])
app.include_router(checkups_router, prefix="/checkups", tags=["Checkups"])
app.include_router(afi_router, prefix="/afi", tags=["Appointments"])
app.include_router(fis_router, prefix="/fis", tags=["Finance"])
app.include_router(cis_router, prefix="/cis", tags=["CIS"])

# Timeline
app.include_router(timeline_router, prefix="/api", tags=["Timeline"])

# Auth
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# Reports (PDF)
app.include_router(report_router, prefix="/reports", tags=["Reports"])

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Clinic API is live 🚀"
    }

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"ok": True}