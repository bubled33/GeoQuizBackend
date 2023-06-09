from enum import Enum
from typing import List
from uuid import uuid4

import bcrypt
from beanie import Document, PydanticObjectId
from pydantic import EmailStr, BaseModel
from redis.asyncio.client import Redis

from untils.role_manager import Role, RoleCarrier
from untils.roles import user_role


class Token(BaseModel):
    access_token: str


class UserStatuses(str, Enum):
    not_verify = 'NOT_VERIFY'
    active = 'ACTIVE'


class User(Document, RoleCarrier):
    email: EmailStr
    username: str
    hashed_password: str
    status: UserStatuses = UserStatuses.not_verify
    roles: List[str] = [user_role.tag]

    def has_role(self, role: Role) -> bool:
        return role.tag in self.roles

    def has_permission(self, permission: str):
        for role in self.roles:
            if self._role_manager.get(role).has_permission(permission):
                return True
        return False

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

    async def terminate_all(self, redis: Redis):

        async for key in redis.scan_iter():
            if 'Auth' not in key.decode('utf-8'):
                continue
            if (await redis.get(key)).decode('utf-8') == str(self.id):
                await redis.delete(key)

    async def login(self, redis: Redis) -> Token:
        token = uuid4()
        await redis.set(f'Auth-{token}', str(self.id))
        return Token(access_token=str(token))

    @property
    def to_out(self) -> 'OutUser':
        return OutUser(
            email=self.email,
            username=self.username,
            roles=self.roles,
            user_id=self.id
        )


class InUser(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        schema_extra = {'description': 'Входная модель пользователя',
                        'example': {
                            'username': 'example_user',
                            'password': 'password',
                            'email': 'example@gmail.com'
                        }}


class OutUser(BaseModel):
    email: EmailStr
    username: str
    roles: List[str]

    user_id: PydanticObjectId

    class Config:
        schema_extra = {
            'description': 'Выходная модель пользователя',
            'example': {
                'email': 'example@gmail.com',
                'username': 'example_user',
                'roles': ['admin', 'user'],
                'user_id': '641526320dabd6c5f784cef5'
            }}
