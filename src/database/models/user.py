from enum import Enum
from typing import List

import bcrypt
from beanie import Document
from pydantic import EmailStr

from src.untils.role_manager import Role, Permissions, RoleCarrier
from src.untils.roles import user_role


class UserStatuses(str, Enum):
    not_verify = 'NOT_VERIFY'
    active = 'ACTIVEs'


class User(Document, RoleCarrier):
    email: EmailStr
    username: str
    hashed_password: str
    status: UserStatuses = UserStatuses.not_verify
    roles: List[str] = [user_role.tag]

    def has_role(self, role: Role) -> bool:
        return role.tag in self.roles

    def has_permission(self, permission: str):
        return bool(next(role for role in self.roles if self._role_manager.get(role).has_permission(permission)))

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
