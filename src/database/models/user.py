from enum import Enum
from typing import List

from beanie import Document
from pydantic import EmailStr

from src.untils.role_manager import Role, Permissions, RoleCarrier
from src.untils.roles import user_role


class User(Document, RoleCarrier):
    email: EmailStr
    username: str
    password: str
    roles: List[str] = [user_role.tag]

    def has_role(self, role: Role) -> bool:
        return role.tag in self.roles

    def has_permission(self, permission: str):
        return bool(next(role for role in self.roles if self._role_manager.get(role).has_permission(permission)))
