from .general import router as general_router, lifespan
from .authorization import router as authorization_router
__all__ = ['general_router', 'lifespan', 'authorization_router']