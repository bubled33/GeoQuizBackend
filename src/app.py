import asyncio

import uvicorn
from fastapi import FastAPI

from .database import RedisManager, RedisConnectData
from .untils.logger import LoggerGroup, ConsoleLogger, Log
from .handlers import general_router, lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(general_router)


if __name__ == '__main__':
    uvicorn.run(app)