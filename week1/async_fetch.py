# async_example.py
import asyncio
import aiohttp
async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)
# Run
urls = ["https://api.github.com/users/github", ...] * 10
results = asyncio.run(fetch_all(urls))
print(f"Fetched {len(results)} URLs in parallel")