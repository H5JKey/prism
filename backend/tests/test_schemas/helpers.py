from pytest import ExceptionInfo
from pydantic import ValidationError


def assert_validation_error(
    exc_info: ExceptionInfo[ValidationError],
    expected_error_type: str,
    loc_field: str,
) -> None:
    errors = exc_info.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert error["type"] == expected_error_type
    assert error["loc"] == (loc_field,)
