from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.store import PyKVStore
import time

app = FastAPI(title="PyKV Server")

store = PyKVStore()

class KVPair(BaseModel):
    key: str
    value: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/set")
async def set_value(data: KVPair):
    await store.set(data.key, data.value)
    return {"status": "success"}

@app.get("/get/{key}")
async def get_value(key: str):
    value = await store.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"key": key, "value": value}

@app.delete("/delete/{key}")
async def delete_value(key: str):
    if not await store.delete(key):
        raise HTTPException(status_code=404, detail="Key not found")
    return {"status": "deleted"}

@app.get("/keys")
async def list_keys():
    return {"keys": await store.keys()}

@app.get("/stats")
async def stats():
    return {
        "current_keys": len(await store.keys()),
        "capacity": store.cache.capacity
    }

@app.post("/benchmark")
async def benchmark(count: int = 1000):
    start = time.time()
    for i in range(count):
        await store.set(f"bench{i}", str(i))
    return {"time_taken_seconds": time.time() - start}
