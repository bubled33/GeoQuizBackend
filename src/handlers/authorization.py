from uuid import uuid4

import bcrypt
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, BaseModel
from redis.asyncio.client import Redis

from src.database import User
from src.database.models.user import UserStatuses
from src.handlers.depends import get_redis, get_email_manager, get_current_user
from src.untils.email_manager import EmailManager
from src.untils.exceptions import account_already_exists, token_expired, username_already_exists, user_invalid_password, \
    user_not_exists

router = APIRouter(prefix='/authorization')


class Token(BaseModel):
    access_token: str


@router.post('/register')
async def on_register(email: EmailStr, username: str, password: str, redis: Redis = Depends(get_redis),
                      email_manager: EmailManager = Depends(get_email_manager)):
    user = await User.find_one(User.email == email)
    if user and user.status.active:
        return account_already_exists
    if not user:
        user = await User(email=email,
                          username=username,
                          hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())).create()

        token = await email_manager.send_verify_url(email)
    await redis.set(f'Verify-{token}', str(user.id), ex=3000)


@router.get('/verify')
async def on_verify(token: str, redis=Depends(get_redis)):
    redis: Redis
    user_id = (await redis.get(f'Verify-{token}')).decode('utf-8')
    if not user_id:
        return token_expired
    await User.find_one(User.id == PydanticObjectId(user_id)).update_one(Set({User.status: UserStatuses.active}))


@router.get('/verify_change_email')
async def on_verify_change_email(token: str, redis=Depends(get_redis)):
    user_id, email = (await redis.get(f'ChangeEmail-{token}')).decode('utf-8').split(';')
    if not user_id:
        return token_expired
    if await User.find_one(User.email == email):
        return account_already_exists
    await User.find_one(User.id == PydanticObjectId(user_id)).update_one(Set({User.email: email}))


@router.post('/token', response_model=Token)
async def on_login(oauth_form: OAuth2PasswordRequestForm = Depends(), redis: Redis = Depends(get_redis)):
    email, password = oauth_form.username, oauth_form.password
    user = await User.find_one(User.email == email)
    if not user:
        return user_not_exists
    if not user.check_password(password):
        return user_invalid_password
    token = uuid4()
    await redis.set(f'Auth-{token}', str(user.id))
    return Token(access_token=str(token))


@router.post('/change_password')
async def on_change_password(old_password: str, new_password: str, user=Depends(get_current_user),
                             redis: Redis = Depends(get_redis)):
    if not user.check_password(old_password):
        return user_invalid_password
    user.hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    await user.replace()
    async for key in redis.scan_iter():
        if 'Auth' not in key.decode('utf-8'):
            continue
        if (await redis.get(key)).decode('utf-8') == str(user.id):
            await redis.delete(key)


@router.post('/change_username')
async def on_change_username(username: str, user=Depends(get_current_user)):
    user.username = username
    await user.replace()


@router.post('/change_email')
async def on_change_email(email: str, user=Depends(get_current_user),
                          email_manager: EmailManager = Depends(get_email_manager), redis: Redis = Depends(get_redis)):
    token = await email_manager.send_change_email(email)
    if await User.find_one(User.email == email):
        return account_already_exists
    await redis.set(f'ChangeEmail-{token}', f'{user.id};{email}', ex=30000)
