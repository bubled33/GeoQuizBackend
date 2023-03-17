from untils.role_manager import Permissions, Role

"""
Permissions
"""


class UserPermissions(Permissions):
    pass


class AdminPermissions(Permissions):
    pass


class OwnerPermissions(Permissions):
    pass


"""
Roles
"""

user_role = Role(tag='user', permissions=UserPermissions)

admin_role = Role(tag='admin', permissions=AdminPermissions)

owner_role = Role(tag='owner', permissions=OwnerPermissions)
