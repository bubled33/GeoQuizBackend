import asyncio
from database import RedisManager, RedisConnectData

async def main():
    redis_manager = RedisManager(RedisConnectData(
        host='',
        port=123,
        username='',
        password='',
        database=0
    ))

if __name__ == '__main__':
    asyncio.run(main())
