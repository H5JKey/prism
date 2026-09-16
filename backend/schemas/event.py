from pydantic import BaseModel

from schemas.constraints.event import TopicConstraint
from schemas.file import FileLocationCreate
from schemas.render import RenderCreatePayload


class EventBase(BaseModel):
    """
    Схема для работы с outbox.
    """


class EventCreate(EventBase):
    """
    Схема для создания записи о событии в outbox.
    """

    topic: TopicConstraint
    message: dict  # type: ignore[type-arg]


class CreateProjectEvent(BaseModel):
    """
    Схема для события генерация проекта.
    """

    project_id: int
    input: FileLocationCreate
    output: FileLocationCreate
    render: RenderCreatePayload


class RenderGeneratedEvent(BaseModel):
    """
    Схема для события рендер завершен.
    """

    project_id: int
    output: FileLocationCreate


class DLQMessage(BaseModel):
    """
    Схема для json при ошибке обработки
    сообщения в брокере.
    """

    message: dict[str, str | int | bool]
    error: str
