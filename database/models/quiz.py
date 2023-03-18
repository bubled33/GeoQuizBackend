from __future__ import annotations

from enum import Enum
from typing import List

import geopy.distance
from beanie import PydanticObjectId, Document
from fastapi import File, UploadFile
from pydantic import BaseModel
from pydantic_geojson import MultiPointModel, PointModel


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
    answers: List[str] | PointModel
    question_type: QuestionTypes

    min_reward: QuestionCoordinateReward | None = None
    max_reward: QuestionCoordinateReward | None = None
    reward: int | None = None

    is_public: bool = False

    def match_reward(self, title: str | None = None, point: PointModel | None = None) -> int:
        match self.question_type:
            case QuestionTypes.coordinate:
                distance = geopy.distance.geodesic((self.point.coordinates.lat,
                                                    self.point.coordinates.lon),
                                                   (point.coordinates.lat,
                                                    point.coordinates.lon)).m

                if distance < self.min_reward.distance:
                    return 0

                elif distance > self.max_reward.distance:
                    return self.min_reward.reward

                else:

                    k = (self.max_reward.reward - self.min_reward.reward) / (
                            self.max_reward.distance - self.min_reward.distance)

                    reward = self.max_reward.reward - k * (distance - self.min_reward.distance)

                    return round(reward)
            case QuestionTypes.title:
                if title == self.title:
                    return self.reward
                return 0
            case QuestionTypes.valid:
                if point == self.point:
                    return self.reward
                return 0


class InQuiz(BaseModel):
    title: str
    description: str
    questions: List[Question]
    image: UploadFile = File(None)


class EditQuiz(BaseModel):
    title: str | None = None
    description: str | None = None
    questions: List[Question] | None = None
    image: UploadFile = File(None)


class Quiz(Document):
    title: str
    is_public: bool = False
    description: str
    questions: List[Question]
    user_id: PydanticObjectId


class OutQuiz(Document):
    title: str
    is_public: bool = False
    description: str
    questions_count: int
    user_id: PydanticObjectId
