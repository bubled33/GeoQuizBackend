from .general import router as general_router, lifespan
from .authorization import router as authorization_router
from .quiz import router as quiz_router
__all__ = ['general_router', 'lifespan', 'authorization_router', 'quiz_router']