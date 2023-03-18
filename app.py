import uvicorn
from fastapi import FastAPI

from handlers import general_router, lifespan, authorization_router, quiz_router

app = FastAPI(lifespan=lifespan)
app.include_router(general_router)
app.include_router(authorization_router)
app.include_router(quiz_router)


if __name__ == '__main__':
    uvicorn.run(app)