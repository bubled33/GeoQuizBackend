import aiofiles
from beanie import PydanticObjectId
from beanie.odm.operators.update.general import Set
from pydantic_geojson._base import Coordinates
from starlette import status

from database.models.quiz import InQuiz, EditQuiz, Quiz

from fastapi import APIRouter, Depends

from handlers.depends import get_current_user, get_quiz
from untils.exceptions import permission_denied

router = APIRouter(prefix='/quiz')


@router.post('/create', status_code=status.HTTP_201_CREATED)
async def on_create_quiz(quiz: InQuiz, user=Depends(get_current_user)):
    image = quiz.image
    quiz = await Quiz(questions=quiz.questions,
                      title=quiz.title,
                      description=quiz.description,
                      user_id=user.id).create()
    if image:
        image_bytes = await image.read()

        async with aiofiles.open(f"images/{quiz.id}.jpg", "wb") as f:
            await f.write(image_bytes)


@router.post('/delete')
async def on_delete_quiz(quiz: Quiz = Depends(get_quiz), user=Depends(get_current_user)):
    if quiz.user_id != user.id:
        if not user.has_permission('delete_quiz'):
            return permission_denied
    await quiz.delete()


@router.post('/edit')
async def on_edit_quiz(edit_quiz: EditQuiz, user=Depends(get_current_user), quiz: Quiz = Depends(get_quiz)):
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


@router.post('/make_public')
async def on_make_public(value: bool, quiz: Quiz = Depends(get_quiz), user=Depends(get_current_user)):
    if not user.has_permission('make_public_quiz'):
        return permission_denied
    await Quiz.find_one(Quiz.id == quiz.id).update_one(Set({Quiz.is_public: value}))

@router.post('/get_all')
async def on_get_all_quiz():
    pass

@router.post('/get')
async def on_get_quiz():
    pass
