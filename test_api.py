import sys
import aiohttp
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://clob.polymarket.com/markets") as r:
            data = await r.json()
            if "data" in data and len(data["data"]) > 0:
                for m in data["data"][:5]:
                    print("Question:", m.get("question", "Unknown"))
                    print("Volume:", m.get("volume", "MISSING"))
                    print("Liquidity:", m.get("liquidity", "MISSING"))

asyncio.run(test())
