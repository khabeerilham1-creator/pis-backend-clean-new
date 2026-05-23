from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.patients import router as patient_router

app = FastAPI(
    title="HDC Dental API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(patient_router)

# ROOT
@app.get("/")
async def root():

    return {
        "message": "HDC Dental API Running Successfully"
    }