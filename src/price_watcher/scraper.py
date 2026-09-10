import asyncio
import json
import aiohttp
from bs4 import BeautifulSoup

async def get_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession(headers=headers, max_line_size=16384, max_field_size=16384) as session:
        async with session.get(url) as resp:
            html = await resp.text()
            print(f"HTML length: {len(html)}, ld+json count: {html.count('application/ld+json')}")

    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")

    for script in scripts:
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue

        candidates = data if isinstance(data, list) else [data]
        for item in candidates:
            if item.get("@type") == "Product":
                offers = item.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0]
                price = offers.get("price")
                if price:
                    return float(price)
    return None

if __name__ == "__main__":
    price = asyncio.run(get_price("PRODUCT_URL_HERE"))
    print(price)