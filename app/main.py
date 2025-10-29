import os
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel

DATA_FILE = "/data/counting.txt"

app = FastAPI()

# ensure data file exists
os.makedirs('/data', exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        f.write('0')

class AddRequest(BaseModel):
    delta: int = 1

async def read_counter() -> int:
    content = await asyncio.to_thread(lambda: open(DATA_FILE, 'r').read().strip())
    return int(content) if content else 0

async def write_counter(value: int):
    tmp_file = DATA_FILE + '.tmp'
    await asyncio.to_thread(lambda: open(tmp_file, 'w').write(str(value)))
    await asyncio.to_thread(os.replace, tmp_file, DATA_FILE)

# Queue ile concurrency kontrolü (max 20)
queue = asyncio.Queue(maxsize=20)

async def process_task(delta: int) -> int:
    async with queue_semaphore:
        count = await read_counter()
        count += delta
        await write_counter(count)
        return count

queue_semaphore = asyncio.Semaphore(20)  # aynı anda 20 task

@app.get("/count")
async def get_count():
    count = await read_counter()
    return {"count": count}

@app.post("/increment")
async def increment():
    async with queue_semaphore:
        count = await read_counter()
        count += 1
        await write_counter(count)
        return {"count": count}

@app.post("/add")
async def add(req: AddRequest):
    if req.delta == 0:
        return {"count": await read_counter()}
    async with queue_semaphore:
        count = await read_counter()
        count += req.delta
        await write_counter(count)
        return {"count": count}
