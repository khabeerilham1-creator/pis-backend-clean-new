from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

app = FastAPI()

# ✅ CORS (FINAL WORKING CONFIG)
origins = [
    "https://clinic-client-lake.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 FORCE HANDLE PREFLIGHT (IMPORTANT)
@app.options("/{full_path:path}")
def preflight_handler(full_path: str):
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "https://clinic-client-lake.vercel.app"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# ✅ TEST ROUTE
@app.get("/")
def home():
    return {"message": "API running 🚀"}


# ✅ LOGIN ROUTE
@app.post("/auth/login")
def login(data: dict):
    username = data.get("username")
    password = data.get("password")

    if username == "admin@hdc.com" and password == "123456":
        return {
            "access_token": "dummy_token",
            "user": username
        }

    return {"error": "Invalid credentials"}