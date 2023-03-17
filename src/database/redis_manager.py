from dataclasses import dataclass

from redis.asyncio.client import Redis

__all__ = ['RedisConnectData', 'RedisManager']

from redis.asyncio.connection import ConnectionPool


@dataclass
class RedisConnectData:
    username: str
    password: str
    host: str
    port: int
    database: int


class RedisManager:
    def __init__(self, connect_data: RedisConnectData):
        self._redis: Redis | None = None
        self._connect_data = connect_data

    @property
    def connection_pool(self) -> ConnectionPool | None:
        if not self._redis:
            return None
        return self._redis.connection_pool

    async def init(self):
        self._redis = Redis(host=self._connect_data.host,
                            port=self._connect_data.port,
                            username=self._connect_data.username,
                            password=self._connect_data.password,
                            )
        await self._redis.initialize()

