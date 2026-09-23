import pytest
from core.constants import TOPIC_MAX_LENGTH
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers import SQLState, assert_sqlstate_code
from tests.test_infrastructure.test_database.test_models.factories import (
    create_outbox,
)


class TestOutbox:
    async def test_outbox_valid(self, session: AsyncSession) -> None:
        outbox = await create_outbox(session)
        assert outbox.id is not None

    @pytest.mark.parametrize("status", ["pending", "sent"])
    async def test_outbox_event_status(
        self,
        session: AsyncSession,
        status: str,
    ) -> None:
        outbox = await create_outbox(session, status=status)
        assert outbox.id is not None

    @pytest.mark.parametrize("status", ["rendering", "completed"])
    async def test_outbox_event_wrong_status(
        self,
        session: AsyncSession,
        status: str,
    ) -> None:
        with pytest.raises(DBAPIError) as exc_info:
            await create_outbox(session, status=status)

        assert_sqlstate_code(exc_info, SQLState.WRONG_ENUM_TYPE)

    @pytest.mark.parametrize(
        "field, value, expected_sqlstate",
        [
            ["topic", "a" * (TOPIC_MAX_LENGTH + 1), SQLState.STRING_TOO_LONG],
        ],
    )
    async def test_outbox_not_valid_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
        expected_sqlstate: str,
    ) -> None:
        params = {field: value}
        with pytest.raises(DBAPIError) as exc_info:
            await create_outbox(session, **params)

        assert_sqlstate_code(exc_info, expected_sqlstate)

    @pytest.mark.parametrize(
        "field, value",
        [
            ["topic", "a" * TOPIC_MAX_LENGTH],
        ],
    )
    async def test_outbox_boundary_field_value(
        self,
        session: AsyncSession,
        field: str,
        value: str,
    ) -> None:
        params = {field: value}
        outbox = await create_outbox(session, **params)
        assert outbox.id is not None

    async def test_outbox_default_event_date(self, session: AsyncSession) -> None:
        outbox = await create_outbox(session, event_date=None)
        assert outbox.id is not None
        assert outbox.event_date is not None
