from json import dumps, loads

from core.logging import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


def serialize_message[T: BaseModel | dict](message_data: T) -> bytes:  # type: ignore[type-arg]
    message_dict = message_data
    if isinstance(message_data, BaseModel):
        message_dict = message_data.model_dump()  # type: ignore[assignment]

    serialized_value = dumps(message_dict)
    encoded_serialized_value = serialized_value.encode()
    return encoded_serialized_value


def deserialize_message(message: bytes) -> dict[str, str | int | bool]:
    message_string = message.decode()
    json_message = loads(message_string)
    return json_message  # type: ignore[no-any-return]
