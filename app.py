import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import settings
from handlers import lifespan, router
app = FastAPI(lifespan=lifespan)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    uvicorn.run(app, host=settings.App.host, port=settings.App.port)
