from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =========================
# IMPORT ROUTES
# =========================
from app.routes.patient import router as patients_router
from app.routes.checkups import router as checkups_router
from app.routes.afi import router as afi_router
from app.routes.fis import router as fis_router
from app.routes.cis import router as cis_router
from app.routes.visits import router as visits_router
from app.routes.invoice import router as invoice_router
from app.routes.report import router as report_router
from app.routes.auth import router as auth_router
from app.routes.lvi import router as lvi_router

# =========================
# APP INIT
# =========================
app = FastAPI(title="Clinic Management API")

# =========================
# CORS FIX (VERY IMPORTANT)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # later secure this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTES REGISTER
# =========================
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

app.include_router(patients_router, prefix="/patients", tags=["Patients"])
app.include_router(checkups_router, prefix="/checkups", tags=["Checkups"])
app.include_router(afi_router, prefix="/afi", tags=["Appointments"])
app.include_router(fis_router, prefix="/fis", tags=["Finance"])
app.include_router(cis_router, prefix="/cis", tags=["CIS"])
app.include_router(visits_router, prefix="/visits", tags=["Visits"])

app.include_router(invoice_router, tags=["Invoice"])   # /invoice, /invoice-pdf
app.include_router(report_router, prefix="/reports", tags=["Reports"])

app.include_router(lvi_router, prefix="/lvi", tags=["LVI"])

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"message": "Clinic API running 🚀"}

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "ok"}