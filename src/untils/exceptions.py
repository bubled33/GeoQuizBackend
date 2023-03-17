from fastapi import HTTPException

account_already_exists = HTTPException(status_code=400, detail="Account already exists!")
