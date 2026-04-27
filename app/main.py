from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://clinic-client-lake.vercel.app"
    ],
    allow_credentials=False,   # 🔥 IMPORTANT CHANGE
    allow_methods=["*"],
    allow_headers=["*"],
)