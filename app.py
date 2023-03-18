import uvicorn
from fastapi import FastAPI

from handlers import lifespan, router
app = FastAPI(lifespan=lifespan)
app.include_router(router)


if __name__ == '__main__':
    uvicorn.run(app)
