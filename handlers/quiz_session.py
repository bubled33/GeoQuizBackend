from typing import List, Union

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
from untils.exceptions import permission_denied, user_not_exists, quiz_not_exists, quiz_session_not_exists

router = APIRouter(prefix='/quiz_session', tags=['API Сессий'], responses={user_not_exists.status_code: {'description': user_not_exists.detail}})


class Reward(BaseModel):
    scores: int = 0

    class Config:
        schema_extra = {
            'description': 'Модель награды за ответ на вопрос',
            'example': {
                'scores': 20
            }}


@router.post('/create', response_model=OutQuizSession, summary='Создать сессию', responses={quiz_not_exists.status_code: {'detail': quiz_not_exists},user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_start(quiz: Quiz = Depends(get_quiz), user=Depends(UserGetter(is_optional=True).get_current_user)):
    if not user and not quiz.is_public:
        raise permission_denied
    quiz_session = await QuizSession(quiz_id=quiz.id, user_id=user.id if user else None).create()
    quiz.history.append(HistoryRow(quiz_session_id=quiz_session.id))
    await quiz.replace()
    return quiz_session.to_out


@router.post('/answer', response_model=Reward, summary='Ответить на текущий вопрос сессии', responses={quiz_session_not_exists.status_code: {'detail': quiz_session_not_exists},user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_answer(title: str | None = Query(default=None, example='Москва'),
                    point: PointModel | MultiPointModel | None = Body(default=None, example=PointModel(
                        coordinates=Coordinates(lon=10.0, lat=10.0))),
                    quiz_session: QuizSession = Depends(get_quiz_session), user: User = Depends(UserGetter(is_optional=True).get_current_user)):
    quiz = await Quiz.get(quiz_session.quiz_id)
    if user and (quiz.user_id != user.id):
        return permission_denied
    question = quiz.questions[quiz_session.current_question - 1]
    scores = question.match_reward(title, point)

    if len(quiz.questions) - quiz_session.current_question > 0:
        await QuizSession.find_one(QuizSession.id == quiz_session.id).update_one(
            Set({QuizSession.current_question: quiz_session.current_question + 1, QuizSession.scores: quiz_session.scores + scores}))
    else:
        await QuizSession.find_one(QuizSession.id == quiz_session.id).update_one(
            Set({QuizSession.status: QuizSessionStatuses.completed, QuizSession.scores: quiz_session.scores + scores}))
    return Reward(scores=scores)


@router.post('/get_all', response_model=List[OutQuizSession], summary='Получить все сессии', responses={user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_get_all_quiz_sessions(user: User = Depends(UserGetter().get_current_user)):
    return [quiz.to_out for quiz in await QuizSession.find().to_list()]


@router.post('/get', response_model=OutQuizSession, summary='Получить сессию по ID', responses={quiz_session_not_exists.status_code: {'detail': quiz_session_not_exists},user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_get_quiz_session(quiz_session: QuizSession = Depends(get_quiz_session),
                              user: User = Depends(UserGetter().get_current_user)):
    return quiz_session.to_out


@router.post('/get_by_user', response_model=List[OutQuizSession], summary='Получить сессии пользователя', responses={user_not_exists.status_code: {'description': user_not_exists.detail}})
async def get_all_by_user(user_id: PydanticObjectId = Query(example='641526320dabd6c5f784cef5'),
                          user: User = Depends(UserGetter().get_current_user)):
    return [quiz.to_out for quiz in await QuizSession.find(QuizSession.user_id == user_id).to_list()]


@router.post('/get_by_quiz', response_model=List[OutQuizSession], summary='Получить все сессии викторины', responses={quiz_not_exists.status_code: {'detail': quiz_not_exists},user_not_exists.status_code: {'description': user_not_exists.detail}})
async def get_all_by_quiz(quiz: Quiz = Depends(get_quiz), user: User = Depends(UserGetter().get_current_user)):
    return [quiz.to_out for quiz in await QuizSession.find(QuizSession.quiz_id == quiz.id).to_list()]


@router.post('/get_question', response_model=Question | None, summary='Получить текущий вопрос сессии', responses={quiz_session_not_exists.status_code: {'detail': quiz_session_not_exists},user_not_exists.status_code: {'description': user_not_exists.detail}})
async def on_get_question(quiz_session: QuizSession = Depends(get_quiz_session), user: User | None = Depends(UserGetter(is_optional=True).get_current_user)):
    quiz = await Quiz.get(PydanticObjectId(quiz_session.quiz_id))
    if quiz_session.status == QuizSessionStatuses.active:
        return quiz.questions[quiz_session.current_question - 1]
    return None
