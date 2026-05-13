import asyncio


class BaseCache:
    def __init__(self):
        self._lock = asyncio.Lock()