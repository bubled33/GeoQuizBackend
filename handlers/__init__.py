from fastapi import APIRouter

from .general import router as general_router, lifespan
from .authorization import router as authorization_router
from .quiz import router as quiz_router
from .user import router as user_router
from .quiz_session import router as quiz_session_router
router = APIRouter(prefix='/api')
router.include_router(authorization_router)
router.include_router(quiz_router)
router.include_router(user_router)
router.include_router(quiz_session_router)