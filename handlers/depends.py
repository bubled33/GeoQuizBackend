from beanie import PydanticObjectId
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio.client import Redis
from starlette.requests import Request

from src.database import RedisManager, User
from untils.email_manager import EmailManager


def get_redis(request: Request) -> Redis:
    redis_manager: RedisManager = request.app.state.redis_manager
    return Redis(connection_pool=redis_manager.connection_pool)


def get_email_manager(request: Request) -> EmailManager:
    return request.app.state.email_manager


async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl='/authorization/token')),
                           redis=Depends(get_redis)):
    redis: Redis
    print(token)
    user_id = await redis.get(f'Auth-{token}')
    if not user_id:
        return
    return await User.get(PydanticObjectId(user_id.decode('utf-8')))
