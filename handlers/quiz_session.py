from typing import List

from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, Query, Body
from pydantic import BaseModel
from pydantic_geojson import PointModel, MultiPointModel
from pydantic_geojson._base import Coordinates

from database import User
from database.models.quiz import Quiz, Question, HistoryRow
from database.models.quiz_session import QuizSession, QuizSessionStatuses, OutQuizSession
from handlers.depends import get_quiz, get_quiz_session, UserGetter

router = APIRouter(prefix='/quiz_session', tags=['API Сессий'])


class Reward(BaseModel):
    scores: int = 0

    class Config:
        schema_extra = {
            'description': 'Модель награды за ответ на вопрос',
            'example': {
                'scores': 20
            }}


@router.post('/create', response_model=OutQuizSession, summary='Создать сессию')
async def on_start(quiz: Quiz = Depends(get_quiz), user=Depends(UserGetter().get_current_user)):
    quiz_session = await QuizSession(quiz_id=quiz.id, user_id=user.id).create()
    quiz.history.append(HistoryRow(quiz_session_id=quiz_session.id))
    await quiz.replace()
    return quiz_session.to_out


@router.post('/answer', response_model=Reward, summary='Ответить на текущий вопрос сессии')
async def on_answer(title: str | None = Query(default=None, example='Москва'),
                    point: PointModel | MultiPointModel | None = Body(default=None, example=PointModel(
                        coordinates=Coordinates(lon=10.0, lat=10.0))),
                    quiz_session: QuizSession = Depends(get_quiz_session)):
    quiz = await Quiz.get(quiz_session.quiz_id)
    question = quiz.questions[quiz_session.current_question - 1]
    scores = question.match_reward(title, point)

    if len(quiz.questions) - quiz_session.current_question > 0:
        await QuizSession.find_one(QuizSession.id == quiz_session.id).update_one(
            Set({QuizSession.current_question: quiz_session.current_question + 1}))
    else:
        await QuizSession.find_one(QuizSession.id == quiz_session.id).update_one(
            Set({QuizSession.status: QuizSessionStatuses.completed}))
    return Reward(scores=scores)


@router.post('/get_all', response_model=List[OutQuizSession], summary='Получить все сессии')
async def on_get_all_quiz_sessions(user: User = Depends(UserGetter().get_current_user)):
    return [quiz.to_out for quiz in await QuizSession.find().to_list()]


@router.post('/get', response_model=OutQuizSession, summary='Получить сессию по ID')
async def on_get_quiz_session(quiz_session: QuizSession = Depends(get_quiz_session),
                              user: User = Depends(UserGetter().get_current_user)):
    return quiz_session.to_out


@router.post('/get_by_user', response_model=List[OutQuizSession], summary='Получить сессии пользователя')
async def get_all_by_user(user_id: PydanticObjectId = Query(example='641526320dabd6c5f784cef5'),
                          user: User = Depends(UserGetter().get_current_user)):
    return [quiz.to_out for quiz in await QuizSession.find(QuizSession.user_id == user_id).to_list()]


@router.post('/get_by_quiz', response_model=List[OutQuizSession], summary='Получить все сессии викторины')
async def get_all_by_quiz(quiz: Quiz = Depends(get_quiz), user: User = Depends(UserGetter().get_current_user)):
    return [quiz.to_out for quiz in await QuizSession.find(QuizSession.quiz_id == quiz.id).to_list()]


@router.post('/get_question', response_model=Question, summary='Получить текущий вопросы сессии')
async def on_get_question(quiz_session: QuizSession = Depends(get_quiz_session)):
    quiz = await Quiz.get(PydanticObjectId(quiz_session.quiz_id))
    if quiz_session.status == QuizSessionStatuses.active:
        return quiz.questions[quiz_session.current_question - 1]
    return None
