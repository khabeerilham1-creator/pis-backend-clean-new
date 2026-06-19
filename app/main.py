from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.patients import router as patient_router
from app.routes.login import router as login_router
from app.routes.inventory import router as inventory_router
from app.routes.expenses import router as expenses_router

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

@app.get("/")
async def root():

    return {
        "message": "API Running"
    }
