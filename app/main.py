from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ROUTES
from app.routes.auth import router as auth_router
from app.routes.patient import router as patient_router
from app.routes.checkup import router as checkup_router
from app.routes.report import router as report_router
from app.routes.invoice import router as invoice_router
from app.routes.afi import router as afi_router
from app.routes.cis import router as cis_router
from app.routes.dashboard import router as dashboard_router
from app.routes.lvi import router as lvi_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# STATIC
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ROUTES
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(checkup_router)
app.include_router(report_router)
app.include_router(invoice_router)
app.include_router(afi_router)
app.include_router(cis_router)
app.include_router(dashboard_router)
app.include_router(lvi_router)


@app.get("/")
def root():
    return {"msg": "HDC System Running 🚀"}