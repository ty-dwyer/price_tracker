import os

import aiohttp
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


async def send_notification(message: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL, json={"content": message}) as resp:
            resp.raise_for_status()