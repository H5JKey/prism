import pytest
from core.constants import TOPIC_MAX_LENGTH
from pydantic import ValidationError
from schemas.event import (
    CreateProjectEvent,
    DLQMessage,
    EventCreate,
    RenderGeneratedEvent,
)
from schemas.file import FileLocationCreate
from schemas.render import RenderCreatePayload

from tests.test_schemas.helpers import assert_validation_error


class TestEventCreate:
    def test_event_create_valid(self, event_create_data: dict[str, str | dict]) -> None:
        event_create = EventCreate(**event_create_data)
        assert event_create.topic == event_create_data["topic"]
        assert event_create.message == event_create_data["message"]

    def test_event_create_has_boundary_topic_length(
        self,
        event_create_data: dict[str, str | dict],
    ) -> None:
        topic = "a" * TOPIC_MAX_LENGTH
        event_create_data["topic"] = topic
        event_create = EventCreate(**event_create_data)
        assert event_create.topic == event_create_data["topic"]
        assert event_create.message == event_create_data["message"]

    def test_event_create_too_long_topic_length(
        self,
        event_create_data: dict[str, str | dict],
    ) -> None:
        topic = "a" * (TOPIC_MAX_LENGTH + 1)
        event_create_data["topic"] = topic
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(**event_create_data)

        assert_validation_error(
            exc_info,
            "string_too_long",
            "topic",
        )

    def test_event_create_needs_message_field(
        self,
        event_create_data: dict[str, str | dict],
    ) -> None:
        event_create_data.pop("message")
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(**event_create_data)

        assert_validation_error(
            exc_info,
            "missing",
            "message",
        )


class TestCreateProjectEvent:
    def test_create_project_event_valid(self, create_project_event_data: dict) -> None:
        create_project_event = CreateProjectEvent.model_validate(
            create_project_event_data,
        )
        assert (
            create_project_event.project_id == create_project_event_data["project_id"]
        )
        assert isinstance(create_project_event.input, FileLocationCreate)
        assert isinstance(create_project_event.output, FileLocationCreate)
        assert isinstance(create_project_event.render, RenderCreatePayload)

    @pytest.mark.parametrize(
        "field",
        [
            "project_id",
            "input",
            "output",
            "render",
        ],
        ids=[
            "Field project_id required",
            "Field input required",
            "Field output required",
            "Field render required",
        ],
    )
    def test_create_project_event_has_required_fields(
        self,
        create_project_event_data: dict[str, str | dict],
        field: str,
    ) -> None:
        create_project_event_data.pop(field)
        with pytest.raises(ValidationError) as exc_info:
            CreateProjectEvent.model_validate(create_project_event_data)

        assert_validation_error(
            exc_info,
            "missing",
            field,
        )


class TestRenderGeneratedEvent:
    def test_render_generated_event_valid(
        self,
        render_generated_event_data: dict[str, int | dict[str, str]],
    ) -> None:
        render_generated_event = RenderGeneratedEvent.model_validate(
            render_generated_event_data,
        )
        assert (
            render_generated_event.project_id
            == render_generated_event_data["project_id"]
        )
        assert isinstance(render_generated_event.output, FileLocationCreate)

    def test_render_generated_event_needs_project_id_field(
        self,
        render_generated_event_data: dict[str, int | dict[str, str]],
    ) -> None:
        render_generated_event_data.pop("project_id")
        with pytest.raises(ValidationError) as exc_info:
            RenderGeneratedEvent.model_validate(render_generated_event_data)

        assert_validation_error(
            exc_info,
            "missing",
            "project_id",
        )

    def test_render_generated_event_needs_output_field(
        self,
        render_generated_event_data: dict[str, int | dict[str, str]],
    ) -> None:
        render_generated_event_data.pop("output")
        with pytest.raises(ValidationError) as exc_info:
            RenderGeneratedEvent.model_validate(render_generated_event_data)

        assert_validation_error(
            exc_info,
            "missing",
            "output",
        )


class TestDLQMessage:
    def test_dlq_message_valid(
        self,
        dlq_message_data: dict[
            str,
            str | dict[str, str | int | bool],
        ],
    ) -> None:
        dlq_message = DLQMessage(**dlq_message_data)
        assert dlq_message.message == dlq_message_data["message"]
        assert dlq_message.error == dlq_message_data["error"]

    def test_dlq_message_needs_message_field(
        self,
        dlq_message_data: dict[
            str,
            str | dict[str, str | int | bool],
        ],
    ) -> None:
        dlq_message_data.pop("message")
        with pytest.raises(ValidationError) as exc_info:
            DLQMessage(**dlq_message_data)

        assert_validation_error(
            exc_info,
            "missing",
            "message",
        )

    def test_dlq_message_needs_error_field(
        self,
        dlq_message_data: dict[
            str,
            str | dict[str, str | int | bool],
        ],
    ) -> None:
        dlq_message_data.pop("error")
        with pytest.raises(ValidationError) as exc_info:
            DLQMessage(**dlq_message_data)

        assert_validation_error(
            exc_info,
            "missing",
            "error",
        )
