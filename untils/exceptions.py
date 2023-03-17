from fastapi import HTTPException
from fastapi.responses import Response

account_already_exists = HTTPException(status_code=400, detail="Account already exists!")
username_already_exists = HTTPException(status_code=400, detail='username_already_exists')
user_not_exists = HTTPException(status_code=400, detail='User not exists!')
user_invalid_password = HTTPException(status_code=400, detail='Invalid password!')
token_expired = HTTPException(status_code=400, detail='Token was expired!')