from typing import Annotated

from annotated_types import MaxLen
from core.constants import TOPIC_MAX_LENGTH

TopicConstraint = Annotated[
    str,
    MaxLen(
        max_length=TOPIC_MAX_LENGTH,
    ),
]
