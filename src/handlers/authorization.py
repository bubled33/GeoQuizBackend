from fastapi import APIRouter

router = APIRouter(prefix='/authorization')

@router.post('/register')
async def on_register():
    pass

@router.post('/login')
async def on_login():
    pass

@router.post('/change_password')
async def on_change_password():
    pass