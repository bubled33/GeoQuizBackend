from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List

import geopy.distance
from beanie import PydanticObjectId, Document
from fastapi import File, UploadFile
from pydantic import BaseModel, Field
from pydantic_geojson import MultiPointModel, PointModel
from pydantic_geojson._base import Coordinates


class HistoryRow(BaseModel):
    date: datetime = Field(default_factory=datetime.now)
    quiz_session_id: PydanticObjectId


class QuestionCoordinateReward(BaseModel):
    distance: float
    reward: int


class QuestionTypes(str, Enum):
    title = 'TITLE'
    coordinate = 'COORDINATE'
    valid = 'VALID'


class Question(BaseModel):
    title: str
    point: PointModel | MultiPointModel
    answers: List[str] | PointModel | MultiPointModel | None = None
    question_type: QuestionTypes

    min_reward: QuestionCoordinateReward | None = None
    max_reward: QuestionCoordinateReward | None = None
    reward: int | None = None

    def match_reward(self, title: str | None = None, point: PointModel | None = None) -> int:
        match self.question_type:
            case QuestionTypes.coordinate:
                distance = geopy.distance.geodesic((self.point.coordinates.lat,
                                                    self.point.coordinates.lon),
                                                   (point.coordinates.lat,
                                                    point.coordinates.lon)).m

                if distance > self.min_reward.distance:
                    return 0

                elif distance < self.max_reward.distance:
                    return self.max_reward.reward

                else:

                    k = (self.max_reward.reward - self.min_reward.reward) / (
                            self.min_reward.distance - self.max_reward.distance)
                    print(k)
                    reward = self.max_reward.reward - k * (distance - self.max_reward.distance)

                    return round(reward)
            case QuestionTypes.title:
                if title == self.title:
                    return self.reward
                return 0
            case QuestionTypes.valid:

                if point.coordinates.lon == self.point.coordinates.lon and point.coordinates.lat == self.point.coordinates.lat:
                    return self.reward
                return 0

    class Config:
        schema_extra = {
            'description': 'Модель вопроса',
            'example': {
                'title': 'Москва',
                'point': MultiPointModel(
                    coordinates=[Coordinates(lat=10.0, lon=10.0), Coordinates(lat=15.0, lon=15.0),
                                 Coordinates(lat=20.0, lon=20.0)]),
                'answers': PointModel(coordinates=Coordinates(lat=10.0, lon=10.0)),
                'question_type': QuestionTypes.valid,
                'reward': 10,
            },
        }


class InQuiz(BaseModel):
    title: str
    description: str
    questions: List[Question]
    image: UploadFile = File(None)

    class Config:
        schema_extra = {
            'description': 'Объект входных данных викторины',
            "example": {
                'title': 'Географический опрос',
                'description': 'Данная викторина проверит ваши знания по географии!',
                'questions': [
                    {
                        'title': 'Москва',
                        'point': PointModel(coordinates=Coordinates(lat=10.0, lon=10.0)),
                        'answers': ['Москва, Багдад', 'Ерусалим'],
                        'question_type': QuestionTypes.title,
                        'reward': 10,
                    },
                    {
                        'title': 'Москва',
                        'answers': MultiPointModel(
                            coordinates=[Coordinates(lat=10.0, lon=10.0), Coordinates(lat=15.0, lon=15.0),
                                         Coordinates(lat=20.0, lon=20.0)]),
                        'point': PointModel(coordinates=Coordinates(lat=10.0, lon=10.0)),
                        'question_type': QuestionTypes.valid,
                        'reward': 10,
                    },
                    {
                        'title': 'Москва',
                        'point': PointModel(coordinates=Coordinates(lat=10.0, lon=10.0)),
                        'question_type': QuestionTypes.coordinate,
                        'min_reward': {'distance': 1000.0, 'reward': 2},
                        'max_reward': {'distance': 10.0, 'reward': 20},
                    }
                ]
            }
        }


class EditQuiz(BaseModel):
    title: str | None = None
    description: str | None = None
    questions: List[Question] | None = None
    image: UploadFile = File(None)

    class Config:
        schema_extra = {'description': 'Объект изменения викторины',
                        'example': {'title': 'Новый заголовок!', 'description': 'Новое описание!'}, }


class Quiz(Document):
    title: str
    is_public: bool = False
    description: str
    questions: List[Question]
    user_id: PydanticObjectId
    history: List[HistoryRow] = []

    @property
    def to_out(self) -> 'OutQuiz':
        return OutQuiz(
            title=self.title,
            is_public=self.is_public,
            description=self.description,
            questions_count=len(self.questions),
            user_id=self.user_id,
            history=self.history,
            quiz_id=self.id
        )


class OutQuiz(BaseModel):
    title: str
    is_public: bool = False
    description: str
    questions_count: int
    user_id: PydanticObjectId
    history: List[HistoryRow] = []

    quiz_id: PydanticObjectId

    class Config:
        schema_extra = {
            'description': 'Объект выходных данных викторины',
            'example': {
                'title': 'Географический опрос',
                'description': 'Данная викторина проверит ваши знания по географии!',
                'is_public': True,
                'questions_count': 3,
                'user_id': '641526320dabd6c5f784cef5',
                'history': [[datetime.now(), '641526320dabd6c5f784cef5']],
                'quiz_id': '641526320dabd6c5f784cef5'
            }}
