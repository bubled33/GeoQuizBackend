import uuid

import bcrypt
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, Query

from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from redis.asyncio.client import Redis
from starlette import status

from database import User
from database.models.user import UserStatuses, Token, OutUser, InUser
from handlers.depends import get_redis, get_email_manager, UserGetter
from untils.email_manager import EmailManager
from untils.exceptions import user_already_exists, token_expired, user_invalid_password, user_not_exists

router = APIRouter(prefix='/authorization', tags=['API Авторитизации'])


@router.post('/register', status_code=status.HTTP_201_CREATED, summary='Зарегистрироваться')
async def on_register(user_data: InUser, redis: Redis = Depends(get_redis),
                      email_manager: EmailManager = Depends(get_email_manager)):
    user = await User.find_one(User.email == user_data.email)
    if user and user.status.active:
        return user_already_exists
    if not user:
        user = await User(email=user_data.email,
                          username=user_data.username,
                          hashed_password=bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())).create()

    token = await email_manager.send_verify_url(user_data.email)
    await redis.set(f'Verify-{token}', str(user.id), ex=3000)


@router.get('/verify', summary='Верефицировать почту при регистрации по токену')
async def on_verify(token: str = Query(example=uuid.uuid4()), redis: Redis = Depends(get_redis)):
    user_id = (await redis.get(f'Verify-{token}')).decode('utf-8')
    if not user_id:
        return token_expired
    await User.find_one(User.id == PydanticObjectId(user_id)).update_one(Set({User.status: UserStatuses.active}))


@router.get('/verify_change_email', summary='Верефицировать почту при смене по токену')
async def on_verify_change_email(token: str = Query(example=uuid.uuid4()), redis=Depends(get_redis)):
    user_id, email = (await redis.get(f'ChangeEmail-{token}')).decode('utf-8').split(';')
    if not user_id:
        return token_expired
    if await User.find_one(User.email == email):
        return user_already_exists
    await User.find_one(User.id == PydanticObjectId(user_id)).update_one(Set({User.email: email}))


@router.post('/token', response_model=Token, summary='Получить токен авторитизации')
async def on_login(oauth_form: OAuth2PasswordRequestForm = Depends(), redis: Redis = Depends(get_redis)):
    email, password = oauth_form.username, oauth_form.password
    user = await User.find_one(User.email == email)
    if not user:
        return user_not_exists
    if not user.check_password(password):
        return user_invalid_password
    return await user.login(redis)


@router.post('/change_password')
async def on_change_password(old_password: str, new_password: str, user=Depends(UserGetter().get_current_user),
                             redis: Redis = Depends(get_redis)):
    if not user.check_password(old_password):
        return user_invalid_password
    await User.find_one(User.id == user.id).update_one(
        Set({'hashed_password': bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())}))
    await user.terminate_all(redis)


@router.post('/change_email', summary='Начать процедуру смены почты')
async def on_change_email(email: str, user=Depends(UserGetter().get_current_user),
                          email_manager: EmailManager = Depends(get_email_manager), redis: Redis = Depends(get_redis)):
    token = await email_manager.send_change_email(email)
    if await User.find_one(User.email == email):
        return user_already_exists
    await redis.set(f'ChangeEmail-{token}', f'{user.id};{email}', ex=30000)
