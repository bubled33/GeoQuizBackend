import asyncio

import uvicorn
from fastapi import FastAPI

from src.database import RedisManager, RedisConnectData
from src.untils.logger import LoggerGroup, ConsoleLogger, Log
from src.handlers import general_router, lifespan, authorization_router

app = FastAPI(lifespan=lifespan)
app.include_router(general_router)
app.include_router(authorization_router)


if __name__ == '__main__':
    uvicorn.run(app)