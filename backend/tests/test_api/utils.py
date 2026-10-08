from typing import Any


def get_result_json(instance: Any, method: str) -> dict:
    return getattr(instance, method).return_value.model_dump()
