from fastapi import APIRouter, WebSocket
from app.core.database import db
import asyncio

router = APIRouter()

invoices = db["invoices"]
bills = db["bills"]

@router.websocket("/live")
async def acc_live(ws: WebSocket):
    await ws.accept()

    while True:
        revenue = sum(float(i.get("amount", 0)) for i in invoices.find())
        expenses = sum(float(b.get("amount", 0)) for b in bills.find())
        profit = revenue - expenses

        await ws.send_json({
            "revenue": revenue,
            "expenses": expenses,
            "profit": profit
        })

        await asyncio.sleep(2)