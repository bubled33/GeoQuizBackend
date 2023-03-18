from fastapi import HTTPException

user_already_exists = HTTPException(status_code=400, detail="Account already exists!")
user_not_exists = HTTPException(status_code=400, detail='User not exists!')
user_invalid_password = HTTPException(status_code=400, detail='Invalid password!')
token_expired = HTTPException(status_code=400, detail='Token was expired!')

permission_denied = HTTPException(status_code=400, detail='Permission denied!')
user_unauthorized = HTTPException(status_code=401, detail='Unauthorized')