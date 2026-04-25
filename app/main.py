from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 🔥 IMPORT ROUTES
from app.routes import auth, patient, fis, cis, checkup, report, visit, invoice, lvi, afi, dashboard

app = FastAPI()

# 🔥 CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clinic-client-lake.vercel.app",
        "http://localhost:3000"
    ],  # ✅ allow your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 ROUTES
app.include_router(auth.router, prefix="/auth")
app.include_router(patient.router, prefix="/patients")
app.include_router(fis.router, prefix="/fis")
app.include_router(cis.router, prefix="/cis")
app.include_router(checkup.router, prefix="/checkup")
app.include_router(report.router, prefix="/report")
app.include_router(visit.router, prefix="/visits")
app.include_router(invoice.router, prefix="/invoice")
app.include_router(lvi.router, prefix="/lvi")
app.include_router(afi.router, prefix="/appointments")
app.include_router(dashboard.router, prefix="/dashboard")


# 🔥 ROOT (OPTIONAL)
@app.get("/")
def root():
    return {"message": "API running 🚀"}