from typing import Any


def get_result_json(
    instance: Any,
    method: str,
    exclude_unset: bool = False,
) -> dict:
    return getattr(instance, method).return_value.model_dump(
        exclude_unset=exclude_unset,
    )
