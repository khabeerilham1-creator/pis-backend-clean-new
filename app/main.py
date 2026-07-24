from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.patients import router as patient_router
from app.routes.login import router as login_router
from app.routes.inventory import router as inventory_router
from app.routes.expenses import router as expenses_router
from app.routes.dentist_revenue import router as dentist_revenue_router
from app.routes.lab_payments import router as lab_payments_router
from app.routes.daily_expenses import router as daily_expenses_router
from app.routes.account_payables import router as account_payables_router
from app.routes.activity_logs import router as activity_logs_router
from app.routes.appointments import router as appointments_router
from app.routes.messages import router as messages_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patient_router)
app.include_router(login_router)
app.include_router(inventory_router)
app.include_router(expenses_router)
app.include_router(dentist_revenue_router)
app.include_router(lab_payments_router)
app.include_router(daily_expenses_router)
app.include_router(account_payables_router)
app.include_router(activity_logs_router)
app.include_router(appointments_router)
app.include_router(messages_router)

@app.get("/")
async def root():

    return {
        "message": "API Running"
    }
