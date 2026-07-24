import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConfigurationError

load_dotenv()

APP_MODE = os.getenv("APP_MODE", "real").lower()
REAL_DB_URL = (
    os.getenv("MONGO_URL")
    or os.getenv("DEMO_MONGO_URL")
    or "mongodb://localhost:27017"
)
DEMO_DB_URL = os.getenv("DEMO_MONGO_URL", REAL_DB_URL)

if APP_MODE == "demo":
    mongo_url = DEMO_DB_URL
    database_name = os.getenv("DEMO_DB_NAME", "smart_clinic_demo")
    print("DEMO DATABASE ACTIVE")
else:
    mongo_url = REAL_DB_URL
    database_name = os.getenv("DB_NAME", "pis")
    print("REAL DATABASE ACTIVE")

def create_mongo_client(primary_url: str) -> MongoClient:
    try:
        return MongoClient(
            primary_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            connect=False,
        )
    except ConfigurationError as exc:
        fallback_url = os.getenv("LOCAL_MONGO_URL", "mongodb://localhost:27017")

        print(f"Configured MongoDB URL could not be prepared: {exc}")

        if fallback_url == primary_url:
            raise

        print("Falling back to LOCAL_MONGO_URL / localhost MongoDB.")

        return MongoClient(
            fallback_url,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            connect=False,
        )


client = create_mongo_client(mongo_url)

db = client[database_name]


def ensure_indexes():
    try:
        db.patients.create_index("biography.regNo", unique=True, sparse=True)
        db.patients.create_index("biography.patientName")
        db.patients.create_index("biography.mobileNumber")
        db.patients.create_index("createdAt")
        db.inventory.create_index("productName")
        db.inventory.create_index("date")
        db.expenses.create_index("category")
        db.expenses.create_index("date")
        db.expenses.create_index("expenseName")
        db.expenses.create_index("description")
        db.expenses.create_index("shop")
        db.expenses.create_index("vendor")
        db.appointments.create_index("date")
        db.appointments.create_index("time")
        db.appointments.create_index("shiftId")
        db.appointments.create_index("dentistId")
        db.appointments.create_index("clientName")
        db.appointments.create_index("status")
        db.lab_payments.create_index("labName")
        db.lab_payments.create_index("date")
        db.dentist_revenue.create_index("dentistName")
        db.dentist_revenue.create_index("patientId")
        db.dentist_revenue.create_index("updatedAt")
        db.activity_logs.create_index("timestamp")
        db.activity_logs.create_index("role")
        db.messages.create_index("createdAt")
        db.messages.create_index("fromRole")
        db.messages.create_index("toRole")
        db.messages.create_index("read")
    except Exception as exc:
        print(f"Database index setup skipped: {exc}")


ensure_indexes()
