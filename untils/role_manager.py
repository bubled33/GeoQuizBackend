from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Type


class Permissions(str, Enum):
    pass


@dataclass
class Role:
    tag: str
    permissions: Type[Permissions]

    def has_permission(self, permission: str) -> bool:
        try:
            return bool(self.permissions(permission))
        except ValueError:
            return False

    def __eq__(self, other):
        return self.tag == other.tag


class RoleManager:
    def __init__(self, roles: List[Role]):
        self._roles: Dict[str, Role] = {}
        for role in roles:
            self._roles[role.tag] = role

    @property
    def roles(self) -> List[Role]:
        return list(self._roles.values())

    def register(self, role: Role):
        self._roles[role.tag] = role

    def get(self, tag: str) -> Role | None:
        return self._roles.get(tag)


class RoleCarrier:
    @classmethod
    def init_role_manager(cls, role_manager: RoleManager):
        cls._role_manager = role_manager