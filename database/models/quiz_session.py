from beanie import Document, PydanticObjectId


class QuizSessionStatuses:
    completed = 'COMPLETED'
    active = 'ACTIVE'


class QuizSession(Document):
    quiz_id: PydanticObjectId
    user_id: PydanticObjectId
    scores: int = 0
    status: QuizSessionStatuses = QuizSessionStatuses.active
    current_question: int = 1


class OutQuizSession(Document):
    scores: int
    status: QuizSessionStatuses
    current_question: int
