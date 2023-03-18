from typing import List

from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr

from database import User
from database.models.user import OutUser
from handlers.depends import UserGetter
from untils.exceptions import user_not_exists

router = APIRouter(prefix='/user', tags=['API Пользователей'])


@router.post('/change_username', responses={user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_change_username(username: str = Query(default='new_username'), user=Depends(UserGetter().get_current_user)):
    await User.find_one(User.id == user.id).update_one(Set({'username': username}))


@router.post('/get', response_model=OutUser, responses={user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_get_user(email: EmailStr | None = None, user_id: PydanticObjectId | None = None,
                      user: User = Depends(UserGetter().get_current_user)):
    if email:
        user = await User.find_one(User.email == email)
    elif user_id:
        user = await User.find_one(User.id == PydanticObjectId(user_id))
    else:
        return None
    return user.to_out


@router.post('/me', response_model=OutUser, responses={user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_me(user: User = Depends(UserGetter().get_current_user)):
    return user.to_out


@router.post('/get_users', response_model=List[OutUser], responses={user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_get_users(user: User = Depends(UserGetter().get_current_user)):
    return [user.to_out for user in await User.find().to_list()]
