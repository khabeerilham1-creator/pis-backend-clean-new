from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://clinic-client-lake.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ TEST ROUTE
@app.get("/")
def home():
    return {"message": "API running 🚀"}

# ✅ LOGIN ROUTE
@app.post("/auth/login")
def login(data: dict, response: Response):
    username = data.get("username")
    password = data.get("password")

    print("LOGIN:", username, password)

    if username == "owner" and password == "Newtimeline1122":
        response.set_cookie(
            key="token",
            value="mysecrettoken",
            httponly=True,
            secure=True,
            samesite="none"
        )
        return {"success": True}

    return {"success": False}