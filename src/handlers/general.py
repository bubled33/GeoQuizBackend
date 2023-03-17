from contextlib import asynccontextmanager
from urllib import response

from fastapi import APIRouter, FastAPI
from starlette.requests import Request

from src.untils.logger import LoggerGroup, ConsoleLogger, Log

from fastapi.responses import Response

router = APIRouter()

__all__ = ['router']


@router.get('/ping')
async def on_ping():
    return Response(status_code=200)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = LoggerGroup([ConsoleLogger()])
    await logger.log(Log('Сервер запущен!'))
    yield
    await logger.log((Log('Сервер остановлен!')))

async def add_process_time_header(request: Request, call_next):
    logger = LoggerGroup([ConsoleLogger()])
    await logger.log(Log('Сервер запущен!'))
    return response