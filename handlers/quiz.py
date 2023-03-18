import datetime
from typing import List

import aiofiles
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from pydantic_geojson import PointModel, MultiPointModel
from pydantic_geojson._base import Coordinates
from starlette import status

from database import User
from database.models.quiz import InQuiz, EditQuiz, Quiz, OutQuiz, QuestionTypes

from fastapi import APIRouter, Depends, Body, Query

from handlers.depends import UserGetter, get_quiz
from untils.exceptions import permission_denied

router = APIRouter(prefix='/quiz', tags=['API Викторин'])

@router.post('/create', summary='Создать викторину', responses={201: {'model': OutQuiz,  'description': 'Объект созданной викторины'}}, status_code=201)
async def on_create_quiz(quiz: InQuiz, user=Depends(UserGetter().get_current_user)):
    image = quiz.image
    quiz = await Quiz(questions=quiz.questions,
                      title=quiz.title,
                      description=quiz.description,
                      user_id=user.id).create()
    if image:
        image_bytes = await image.read()

        async with aiofiles.open(f"images/{quiz.id}.jpg", "wb") as f:
            await f.write(image_bytes)

    return quiz.to_out
@router.post('/delete', summary='Удалить викторину')
async def on_delete_quiz(quiz: Quiz = Depends(get_quiz), user=Depends(UserGetter().get_current_user)):
    if quiz.user_id != user.id:
        if not user.has_permission('delete_quiz'):
            return permission_denied
    await quiz.delete()


@router.post('/edit', summary='Изменить викторину')
async def on_edit_quiz(edit_quiz: EditQuiz, user=Depends(UserGetter().get_current_user), quiz: Quiz = Depends(get_quiz)):
    if quiz.user_id != user.id:
        if not user.has_permission('edit_quiz'):
            return permission_denied
    edit_fields = edit_quiz.dict(exclude={'image'})
    new_fields = {}
    for key, value in edit_fields.items():
        if not value:
            continue
        new_fields[key] = value
    await Quiz.find_one(Quiz.id == quiz.id).update_one(Set(new_fields))


@router.post('/make_public', summary='Изменить статус публичности')
async def on_make_public(value: bool = Query(example=True), quiz: Quiz = Depends(get_quiz), user=Depends(UserGetter().get_current_user)):
    if not user.has_permission('make_public_quiz'):
        return permission_denied
    await Quiz.find_one(Quiz.id == quiz.id).update_one(Set({Quiz.is_public: value}))


@router.post('/get_public', response_model=List[OutQuiz], summary='Получить все публичные викторины')
async def on_get_public_quiz():
    return [quiz.to_out for quiz in await Quiz.find(Quiz.is_public == True).to_list()]


@router.post('/get_by_user', response_model=List[OutQuiz], summary='Получить все викторины пользователя')
async def on_get_by_user(user_id: PydanticObjectId = Query(example='641526320dabd6c5f784cef5'), user: User = Depends(UserGetter().get_current_user)):
    all_quiz = await Quiz.find(Quiz.user_id == PydanticObjectId(user_id)).to_list()
    all_quiz = [quiz.to_out for quiz in all_quiz]

    if user.id == user_id:
        return all_quiz
    return all_quiz


@router.post('/get', response_model=OutQuiz, summary='Получить викторину по ID')
async def on_get_quiz(quiz = Depends(get_quiz), user: User = Depends(UserGetter().get_current_user)):
    return quiz.to_out
