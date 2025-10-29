import asyncio
import httpx

CONCURRENCY = 50  # Toplam istek sayısı
URLS = [
    'http://localhost:8000/increment',  # app1
    'http://localhost:8001/increment',  # app2
]

async def hit(url, retries=10, delay=0.05):
    async with httpx.AsyncClient() as client:
        for _ in range(retries):
            try:
                r = await client.post(url, timeout=10.0)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                await asyncio.sleep(delay)
        return {'error': 'Failed after retries'}

async def worker(url, n):
    tasks = [hit(url) for _ in range(n)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

async def main():
    per_url = CONCURRENCY // len(URLS)
    tasks = [worker(url, per_url) for url in URLS]
    all_results = await asyncio.gather(*tasks)

    flat_results = [item for sublist in all_results for item in sublist]
    successes = sum(1 for r in flat_results if 'count' in r)
    failures = sum(1 for r in flat_results if 'error' in r or 'detail' in r)

    print(f"Toplam istek: {len(flat_results)}")
    print(f"Başarılı: {successes}, Hatalı: {failures}")
    print("Son 10 sonuç:", flat_results[-10:])

if __name__ == '__main__':
    asyncio.run(main())
