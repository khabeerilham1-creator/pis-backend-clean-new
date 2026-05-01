from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ROUTES
from app.routes.patient import router as patients_router
from app.routes.checkup import router as checkups_router
from app.routes.afi import router as afi_router
from app.routes.fis import router as fis_router
from app.routes.cis import router as cis_router
from app.routes.timeline import router as timeline_router
from app.routes.auth import router as auth_router
from app.routes.report import router as report_router

app = FastAPI(title="Clinic Management API")

# 🔥 CORS (UNBLOCK EVERYTHING FOR NOW)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STATIC FILES
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ROUTES
app.include_router(patients_router, prefix="/patients")
app.include_router(checkups_router, prefix="/checkups")
app.include_router(afi_router, prefix="/afi")
app.include_router(fis_router, prefix="/fis")
app.include_router(cis_router, prefix="/cis")
app.include_router(timeline_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
app.include_router(report_router, prefix="/reports")

@app.get("/")
def root():
    return {"status": "running"}