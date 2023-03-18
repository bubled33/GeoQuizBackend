from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from config import settings
from database import User
from database.models.quiz import Quiz
from untils.email_manager import EmailManager
from untils.logger import LoggerGroup, ConsoleLogger, Log
from untils.roles import user_role, admin_role, owner_role
from untils.role_manager import RoleManager

from database import RedisManager, BeanieManager, RedisConnectData, BeanieConnectData
from fastapi.responses import Response

router = APIRouter()

__all__ = ['router']


@router.get('/ping')
async def on_ping():
    return Response(status_code=200)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = LoggerGroup([ConsoleLogger()])
    app.state.logger = logger

    role_manager = RoleManager(roles=[user_role, owner_role, admin_role])
    redis_manager = RedisManager(
        connect_data=RedisConnectData(
            username=settings.Redis.username,
            password=settings.Redis.password,
            host=settings.Redis.host,
            port=settings.Redis.port,
            database=settings.Redis.database
        ))
    beanie_manager = BeanieManager(
        connect_data=BeanieConnectData(
            username=settings.MongoDB.username,
            password=settings.MongoDB.password,
            host=settings.MongoDB.host,
            port=settings.MongoDB.port,
            database=settings.MongoDB.database
        ), models=[User, Quiz], role_manager=role_manager)

    await beanie_manager.init()
    app.state.beanie_manager = beanie_manager
    await logger.log(Log('MongoDB проинициализирована'))

    await redis_manager.init()
    app.state.redis_manager = redis_manager
    await logger.log(Log('Redis проинициализирована'))

    email_manager = EmailManager(username=settings.Email.username, password=settings.Email.password)
    app.state.email_manager = email_manager
    await logger.log(Log('EmailManager проинициализирован'))

    await email_manager.init()
    await logger.log(Log('Сервер запущен!'))

    yield

    await logger.log((Log('Сервер остановлен!')))
