from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTES
from app.routes.patient import router as patients_router
from app.routes.checkups import router as checkups_router
from app.routes.afi import router as afi_router
from app.routes.fis import router as fis_router
from app.routes.cis import router as cis_router
from app.routes.auth import router as auth_router
from app.routes.report import router as report_router
from app.routes.invoice import router as invoice_router

app = FastAPI(title="Clinic Management API")


# =========================
# CORS FIX (VERY IMPORTANT)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# INCLUDE ROUTES
# =========================
app.include_router(auth_router, prefix="/auth")
app.include_router(patients_router, prefix="/patients")
app.include_router(checkups_router, prefix="/checkups")
app.include_router(afi_router, prefix="/afi")
app.include_router(fis_router, prefix="/fis")
app.include_router(cis_router, prefix="/cis")
app.include_router(report_router)
app.include_router(invoice_router)


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"message": "Clinic Management API Running 🚀"}