import bcrypt
from fastapi import APIRouter
from pydantic import EmailStr

from src.database import User
from src.untils.exceptions import account_already_exists

router = APIRouter(prefix='/authorization')


@router.post('/register')
async def on_register(email: EmailStr, username:str, password: str):
    user = await User.find_one(User.email == email)
    if user:
        raise account_already_exists

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    user = await User(email=email, username=username, hashed_password=hashed_password)

@router.post('/login')
async def on_login(email: EmailStr):
    pass


@router.post('/change_password')
async def on_change_password():
    pass
