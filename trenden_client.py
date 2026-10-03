import httpx
from config import TREN_DEN_URL, BOT_API_KEY

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import asyncio
import time

PING_TIMEOUT = 10
PING_INTERVAL = 10
WAKE_DEADLINE = 180
POST_TIMEOUT = 30

LOCAL_TZ = ZoneInfo("America/New_York")

async def is_awake() -> bool:
    try:
        async with httpx.AsyncClient(timeout=PING_TIMEOUT) as client:
            r = await client.get(f"{TREN_DEN_URL}/health")
    except httpx.RequestError:
        return False
    return r.status_code == 200

async def wait_for_trenden() -> bool:
    deadline = time.monotonic() + WAKE_DEADLINE
    while time.monotonic() < deadline:
        if await is_awake():
            return True
        await asyncio.sleep(PING_INTERVAL)
    return False            

def format_confirmation(data: dict) -> str:
    # the backend returns a naive datetime that is really UTC
    dt = datetime.fromisoformat(data["date"]).replace(tzinfo=timezone.utc)
    when = dt.astimezone(LOCAL_TZ).strftime("%a, %b %d at %H:%M")

    exercises = data["exercises"]
    total_sets = sum(len(e["sets"]) for e in exercises)

    return (
        f"✅ Imported {data['workout_name']}\n"
        f"{when}\n"
        f"{len(exercises)} exercises, {total_sets} sets"
    )

async def import_workout(text: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=POST_TIMEOUT) as client:
            r = await client.post(
                    f"{TREN_DEN_URL}/import/strong",
                    json={"text": text},
                    headers={"X-API-Key": BOT_API_KEY}
                )
    except httpx.RequestError:
        return "Couldn't reach Trenden."
    
    if r.status_code == 200:
        data = r.json()
        return format_confirmation(data)
    
    if r.status_code == 422:
        detail = r.json().get("detail")
        return f"Couldn't import: {detail}" if isinstance(detail, str) else "Couldn't import: invalid format."

    return f"Something went wrong ({r.status_code})"