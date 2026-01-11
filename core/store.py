import asyncio
from core.lru_cache import LRUCache
from persistence.persistence_manager import PersistenceManager

class PyKVStore:
    def __init__(self, capacity=5):
        self.cache = LRUCache(capacity)
        self.persistence = PersistenceManager()
        self.lock = asyncio.Lock()

        recovered = self.persistence.recover()
        for k, v in recovered.items():
            self.cache.set(k, v)

        self.persistence.start_background_compaction()

    async def get(self, key):
        async with self.lock:
            return self.cache.get(key)

    async def set(self, key, value):
        async with self.lock:
            evicted = self.cache.set(key, value)
            self.persistence.log_set(key, value)
            if evicted:
                self.persistence.log_delete(evicted)

    async def delete(self, key):
        async with self.lock:
            if self.cache.delete(key):
                self.persistence.log_delete(key)
                return True
            return False

    async def keys(self):
        async with self.lock:
            return self.cache.keys()
