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


class RoleAccessData(BaseModel):
    role: str
    accessCode: str
    dentistId: str | None = None


class ShiftAccessData(BaseModel):
    shiftId: str
    accessCode: str


@router.post("/login")
async def login(data: LoginData):
    shift_users = [
        {
            "username": "morning",
            "password": os.getenv("MORNING_SHIFT_PASSWORD", "arabic"),
            "name": "Dr 1",
            "role": "admin",
            "shiftId": "morning",
            "shiftName": "Morning Shift",
            "doctorName": "Dr 1",
        },
        {
            "username": "evening",
            "password": os.getenv("EVENING_SHIFT_PASSWORD", "persian"),
            "name": "Dr 2",
            "role": "admin",
            "shiftId": "evening",
            "shiftName": "Evening Shift",
            "doctorName": "Dr 2",
        },
    ]
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
    ] + shift_users

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

        if matched_user.get("shiftId"):
            token_payload.update(
                {
                    "shiftId": matched_user["shiftId"],
                    "shiftName": matched_user["shiftName"],
                    "doctorName": matched_user["doctorName"],
                }
            )

        token = create_access_token(
            token_payload
        )

        response = {
            "token": token,
            "role": matched_user["role"],
            "username": matched_user["username"],
            "name": matched_user["name"],
        }

        if matched_user.get("shiftId"):
            response.update(
                {
                    "shiftId": matched_user["shiftId"],
                    "shiftName": matched_user["shiftName"],
                    "doctorName": matched_user["doctorName"],
                }
            )

        return response

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/shift-access")
async def shift_access(data: ShiftAccessData):
    shift_id = (data.shiftId or "").strip().lower()
    access_code = (data.accessCode or "").strip()

    shift_rules = {
        "morning": {
            "password": os.getenv("MORNING_SHIFT_PASSWORD", "arabic"),
            "shiftName": "Morning Shift",
            "doctorName": "Dr 1",
        },
        "evening": {
            "password": os.getenv("EVENING_SHIFT_PASSWORD", "persian"),
            "shiftName": "Evening Shift",
            "doctorName": "Dr 2",
        },
    }

    shift = shift_rules.get(shift_id)

    if not shift or access_code != shift["password"]:
        raise HTTPException(status_code=401, detail="Invalid shift code")

    return {
        "shiftId": shift_id,
        "shiftName": shift["shiftName"],
        "doctorName": shift["doctorName"],
    }


@router.post("/role-access")
async def role_access(data: RoleAccessData):
    requested_role = (data.role or "").strip().lower()
    dentist_id = (data.dentistId or "").strip().lower()
    access_code = (data.accessCode or "").strip()

    role_access_rules = {
        "receptionist": {
            "password": os.getenv("RECEPTIONIST_ROLE_PASSWORD", "receipisnist"),
            "name": os.getenv("RECEPTIONIST_ROLE_NAME", "Reception Desk"),
            "role": "receptionist",
        },
        "admin": {
            "password": os.getenv("ADMIN_ROLE_PASSWORD", "newtimeline"),
            "name": os.getenv("ADMIN_ROLE_NAME", "Admin"),
            "role": "admin",
        },
    }

    dentist_rules = {
        "dr-tufyl": {
            "password": os.getenv("DR_TUFYL_ROLE_PASSWORD", "good morning"),
            "name": "Dr Tufyl",
        },
        "dr-abdur-rehman": {
            "password": os.getenv("DR_ABDUR_REHMAN_ROLE_PASSWORD", "dentist"),
            "name": "Dr Abdur Rehman",
        },
    }

    if requested_role == "dentist":
        dentist = dentist_rules.get(dentist_id)

        if not dentist or access_code != dentist["password"]:
            raise HTTPException(status_code=401, detail="Invalid access code")

        return {
            "role": "dentist",
            "name": dentist["name"],
            "dentistId": dentist_id,
            "dentistName": dentist["name"],
        }

    rule = role_access_rules.get(requested_role)

    if not rule or access_code != rule["password"]:
        raise HTTPException(status_code=401, detail="Invalid access code")

    return {
        "role": rule["role"],
        "name": rule["name"],
    }
