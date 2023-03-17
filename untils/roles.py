
"""
Roles & Permissions
"""
from untils.role_manager import Permissions, Role


class UserPermissions(Permissions):
    ping = 'PING'


user_role = Role(tag='user', permissions=UserPermissions)


class AdminPermissions(Permissions):
    ping = 'PING'


admin_role = Role(tag='admin', permissions=AdminPermissions)


class OwnerPermissions(Permissions):
    ping = 'PING'


owner_role = Role(tag='owner', permissions=OwnerPermissions)
