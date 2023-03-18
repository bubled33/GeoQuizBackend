from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pydantic_geojson import PointModel, MultiPointModel

from database.models.quiz import Quiz
from database.models.quiz_session import QuizSession, QuizSessionStatuses
from handlers.depends import get_quiz, get_quiz_session, get_current_user

router = APIRouter()


class Reward(BaseModel):
    scores: int = 0


@router.post('/create')
async def on_start(quiz: Quiz = Depends(get_quiz), user = Depends(get_current_user)):
    await QuizSession(quiz_id=quiz.id, user_id=user.id).create()


@router.post('/answer', response_model=Reward)
async def on_answer(title: str, point: PointModel | MultiPointModel,
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
@router.post('/get_all')
async def on_get_all_quiz_sessions():
    pass

@router.post('/get')
async def on_get_quiz_session():
    pass

@router.post('/get_question')
async def on_get_question():
    pass
