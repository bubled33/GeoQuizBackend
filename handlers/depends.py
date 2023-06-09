from beanie import PydanticObjectId
from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio.client import Redis
from starlette.requests import Request

from database import RedisManager, User
from database.models.quiz import Quiz
from database.models.quiz_session import QuizSession
from untils.email_manager import EmailManager
from untils.exceptions import user_unauthorized, quiz_not_exists, quiz_session_not_exists
from untils.logger import LoggerGroup


def get_redis(request: Request) -> Redis:
    redis_manager: RedisManager = request.app.state.redis_manager
    return Redis(connection_pool=redis_manager.connection_pool)


def get_email_manager(request: Request) -> EmailManager:
    return request.app.state.email_manager


def get_logger(request: Request) -> LoggerGroup:
    return request.app.state.logger


async def get_quiz(quiz_id: PydanticObjectId = Query(example='641526320dabd6c5f784cef5',
                                                     description='Уникальный ID викторины')) -> Quiz:
    if quiz := await Quiz.get(quiz_id):
        return quiz
    raise quiz_not_exists


async def get_quiz_session(quiz_session_id: PydanticObjectId = Query(example='641526320dabd6c5f784cef5',
                                                                     description='Уникальный ID сессии викторины')) -> QuizSession:
    if quiz_session := await QuizSession.get(quiz_session_id):
        return quiz_session
    raise quiz_session_not_exists


class UserGetter:
    def __init__(self, is_optional: bool = False):
        if is_optional:
            self.get_current_user = self._get_current_user_optional
        if not is_optional:
            self.get_current_user = self._get_current_user

    async def _get_current_user(self, token: str | None = Depends(
                                          OAuth2PasswordBearer(tokenUrl='/api/authorization/token', auto_error=True)),
                                      redis: Redis = Depends(get_redis)):
        return await self._get_user_by_token(token, redis)
    async def _get_current_user_optional(self,token: str | None = Depends(
                                          OAuth2PasswordBearer(tokenUrl='/api/authorization/token', auto_error=False)),
                                      redis: Redis = Depends(get_redis)):
        if token:
            return await self._get_user_by_token(token, redis)
        return None

    async def _get_user_by_token(self, token: str, redis: Redis) -> User:
        user_id = await redis.get(f'Auth-{token}')
        if not user_id:
            raise user_unauthorized
        return await User.get(PydanticObjectId(user_id.decode('utf-8')))
