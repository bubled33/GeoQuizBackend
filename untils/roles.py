from untils.role_manager import Permissions, Role

"""
Permissions
"""


class UserPermissions(Permissions):
    pass


class AdminPermissions(Permissions):
    make_public_quiz = 'make_public_quiz'


class OwnerPermissions(Permissions):
    make_public_quiz = 'make_public_quiz'


"""
Roles
"""

user_role = Role(tag='user', permissions=UserPermissions)

admin_role = Role(tag='admin', permissions=AdminPermissions)

owner_role = Role(tag='owner', permissions=OwnerPermissions)
