import os

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.security import create_access_token

load_dotenv()

router = APIRouter()


class LoginData(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(data: LoginData):
    users = [
        {
            "username": os.getenv("ADMIN_USERNAME", "hdc1122"),
            "password": os.getenv("ADMIN_PASSWORD", "drzaffar"),
            "name": os.getenv("ADMIN_NAME", "HDC Admin"),
            "role": "admin",
        },
        {
            "username": os.getenv("RECEPTIONIST_USERNAME", "receptionist"),
            "password": os.getenv("RECEPTIONIST_PASSWORD", "reception123"),
            "name": os.getenv("RECEPTIONIST_NAME", "Reception Desk"),
            "role": "receptionist",
        },
        {
            "username": os.getenv("DOCTOR_USERNAME", "doctor"),
            "password": os.getenv("DOCTOR_PASSWORD", "doctor123"),
            "name": os.getenv("DOCTOR_NAME", "Dr Zaffar Iqbal"),
            "role": "doctor",
        },
    ]

    matched_user = next(
        (
            user
            for user in users
            if data.username == user["username"] and data.password == user["password"]
        ),
        None,
    )

    if matched_user:
        token_payload = {
            "sub": matched_user["username"],
            "username": matched_user["username"],
            "name": matched_user["name"],
            "role": matched_user["role"],
        }

        token = create_access_token(
            token_payload
        )

        response = {
            "token": token,
            "role": matched_user["role"],
            "username": matched_user["username"],
            "name": matched_user["name"],
        }

        return response

    raise HTTPException(status_code=401, detail="Invalid credentials")
