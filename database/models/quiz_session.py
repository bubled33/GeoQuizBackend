from datetime import datetime
from enum import Enum
from typing import Dict

from beanie import Document, PydanticObjectId
from pydantic import BaseModel


class QuizSessionStatuses(str, Enum):
    completed = 'COMPLETED'
    active = 'ACTIVE'


class QuizSession(Document):
    quiz_id: PydanticObjectId

    user_id: PydanticObjectId | None = None
    username: str | None = None

    scores: int = 0
    status: QuizSessionStatuses = QuizSessionStatuses.active
    current_question: int = 1

    @property
    def to_out(self) -> 'OutQuizSession':
        return OutQuizSession(
            scores=self.scores,
            satus=self.status,
            current_question=self.current_question,
            user_id=self.user_id,
            username=self.username,
            quiz_session_id = self.id
        )


class OutQuizSession(BaseModel):
    scores: int
    status: QuizSessionStatuses
    current_question: int

    user_id: PydanticObjectId | None = None
    username: str | None = None

    quiz_session_id: PydanticObjectId

    class Config:
        schema_extra = {
            'description': 'Выходная модель сессии викторины',
            'example': {
            'current_question': 3,
            'user_id': '641526320dabd6c5f784cef5',
            'scores': 12,
            'status': QuizSessionStatuses.active,
            'quiz_session_id': '641526320dabd6c5f784cef5'
        }}

