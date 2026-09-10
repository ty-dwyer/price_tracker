import asyncio
import json
from pathlib import Path

from .scraper import get_price
from .notifier import send_notification


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
STORAGE_PATH = PROJECT_ROOT / "storage.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)
    
def load_storage():
    if not STORAGE_PATH.exists():
        return {}
    with open(STORAGE_PATH, "r") as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)

def save_storage(storage):
    with open(STORAGE_PATH, "w") as f:
        json.dump(storage, f, indent=2)

async def check_product(product, storage):
    product_id = product["id"]
    name = product["name"]
    url = product["url"]
    target_price = product["target_price"]

    try:
        current_price = await get_price(url)
    except Exception as e:
        print(f"[{name}] failed to fetch price: {e}")
        return

    if current_price is None:
        print(f"[{name}] could not extract price")
        return

    entry = storage.get(product_id, {"last_price": None, "notified": False})

    print(f"[{name}] current price: {current_price} (target: {target_price})")

    if current_price <= target_price:
        if not entry["notified"]:
            message = (
                f"🔥 **{name}** is on sale!\n"
                f"Price: ${current_price:.2f} (target: ${target_price:.2f})\n"
                f"{url}"
            )
            await send_notification(message)
            entry["notified"] = True
    else:
        entry["notified"] = False

    entry["last_price"] = current_price
    storage[product_id] = entry


async def main_async():
    config = load_config()
    storage = load_storage()

    for product in config:
        await check_product(product, storage)

    save_storage(storage)


if __name__ == "__main__":
    asyncio.run(main_async())