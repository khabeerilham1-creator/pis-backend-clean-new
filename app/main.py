from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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

# NEW MODULES
from app.routes.hai import router as hai_router
from app.routes.debtors import router as debtors_router
from app.routes.creditors import router as creditors_router
from app.routes.bills import router as bills_router
from app.routes.acc import router as acc_router
from app.routes.acc_ws import router as acc_ws_router

# 🔥 PERMISSIONS
from app.routes.permissions import router as permissions_router

# 🔥 ACCOUNT STATUS
from app.routes.account_status import router as account_status_router

# 🌍 CITY PATIENTS
from app.routes.city_patients import router as city_patients_router


# =========================
# APP INIT
# =========================
app = FastAPI(
    title="Clinic Management API"
)


# =========================
# STATIC FILES
# =========================
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)


# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "https://drzaffariqbal.com",
        "https://www.drzaffariqbal.com",
        "http://localhost:3000"
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ROUTES
# =========================

# AUTH
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)

# CORE
app.include_router(
    patients_router,
    prefix="/patients",
    tags=["Patients"]
)

app.include_router(
    checkups_router,
    prefix="/checkups",
    tags=["Checkups"]
)

app.include_router(
    visits_router,
    prefix="/visits",
    tags=["Visits"]
)

# CLINICAL
app.include_router(
    afi_router,
    prefix="/afi",
    tags=["AFI"]
)

app.include_router(
    cis_router,
    prefix="/cis",
    tags=["CIS"]
)

app.include_router(
    prescription_router,
    prefix="/prescription",
    tags=["Prescription"]
)

# FINANCE
app.include_router(
    fis_router,
    prefix="/fis",
    tags=["FIS"]
)

app.include_router(
    invoice_router,
    prefix="/invoice",
    tags=["Invoice"]
)

app.include_router(
    lvi_router,
    prefix="/lvi",
    tags=["LVI"]
)

# 🔥 ACCOUNT STATUS
app.include_router(
    account_status_router,
    prefix="/account-status",
    tags=["Account Status"]
)

# 🌍 CITY PATIENTS
app.include_router(
    city_patients_router,
    prefix="/city-patients",
    tags=["City Patients"]
)

# REPORTS
app.include_router(
    reports_router,
    prefix="/reports",
    tags=["Reports"]
)

app.include_router(
    patient_files_router,
    prefix="/patient-files",
    tags=["Patient Files"]
)

# TIMELINE
app.include_router(
    timeline_router,
    prefix="/timeline",
    tags=["Timeline"]
)

# DASHBOARD
app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

# AI
app.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI"]
)

# UPLOAD
app.include_router(
    upload_router,
    prefix="/upload",
    tags=["Upload"]
)

# INTELLIGENCE
app.include_router(
    acc_router,
    prefix="/acc",
    tags=["ACC"]
)

app.include_router(
    hai_router,
    prefix="/hai",
    tags=["HAI"]
)

# CONTROL
app.include_router(
    debtors_router,
    prefix="/debtors",
    tags=["Debtors"]
)

app.include_router(
    creditors_router,
    prefix="/creditors",
    tags=["Creditors"]
)

app.include_router(
    bills_router,
    prefix="/bills",
    tags=["Bills"]
)

# REALTIME
app.include_router(
    acc_ws_router,
    prefix="/acc"
)

# 🔥 PERMISSIONS
app.include_router(
    permissions_router,
    prefix="/permissions",
    tags=["Permissions"]
)


# =========================
# ROOT
# =========================
@app.get("/")
def root():

    return {
        "msg": "Clinic API Running 🚀"
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }