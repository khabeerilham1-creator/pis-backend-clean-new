from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =========================
# IMPORT ROUTES
# =========================
from app.routes.auth import router as auth_router
from app.routes.patients import router as patients_router
from app.routes.checkups import router as checkups_router
from app.routes.visits import router as visits_router
from app.routes.afi import router as afi_router
from app.routes.cis import router as cis_router
from app.routes.fis import router as fis_router
from app.routes.invoice import router as invoice_router
from app.routes.reports import router as reports_router
from app.routes.lvi import router as lvi_router
from app.routes.timeline import router as timeline_router
from app.routes.patient_files import router as patient_files_router
from app.routes.dashboard import router as dashboard_router
from app.routes.ai import router as ai_router
from app.routes.upload import router as upload_router
from app.routes.prescription import router as prescription_router

# 🔥 NEW MODULES
from app.routes.hai import router as hai_router
from app.routes.debtors import router as debtors_router
from app.routes.creditors import router as creditors_router
from app.routes.bills import router as bills_router
from app.routes.acc import router as acc_router

# 🔥🔥 NEW REALTIME ROUTER (ADDED ONLY)
from app.routes.acc_ws import router as acc_ws_router


# =========================
# APP INIT
# =========================
app = FastAPI(title="Clinic Management API")


# =========================
# CORS (🔥 FIXED FOR DOMAIN)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://drzaffariqbal.com",
        "https://www.drzaffariqbal.com",
        "http://localhost:3000"  # ✅ keep for local testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROUTES
# =========================

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

app.include_router(patients_router, prefix="/patients", tags=["Patients"])
app.include_router(checkups_router, prefix="/checkups", tags=["Checkups"])
app.include_router(visits_router, prefix="/visits", tags=["Visits"])

app.include_router(afi_router, prefix="/afi", tags=["AFI"])
app.include_router(cis_router, prefix="/cis", tags=["CIS"])

app.include_router(fis_router, prefix="/fis", tags=["FIS"])
app.include_router(invoice_router, prefix="/invoice", tags=["Invoice"])
app.include_router(lvi_router, prefix="/lvi", tags=["LVI"])

app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(patient_files_router, prefix="/patient-files", tags=["Patient Files"])

app.include_router(timeline_router, prefix="/timeline", tags=["Timeline"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(upload_router, prefix="/upload", tags=["Upload"])

app.include_router(prescription_router, prefix="/prescription", tags=["Prescription"])

app.include_router(hai_router, prefix="/hai", tags=["HAI"])
app.include_router(debtors_router, prefix="/debtors", tags=["Debtors"])
app.include_router(creditors_router, prefix="/creditors", tags=["Creditors"])
app.include_router(bills_router, prefix="/bills", tags=["Bills"])
app.include_router(acc_router, prefix="/acc", tags=["ACC"])

# 🔥 REALTIME ROUTE (ADDED)
app.include_router(acc_ws_router, prefix="/acc")


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"msg": "Clinic API Running 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}