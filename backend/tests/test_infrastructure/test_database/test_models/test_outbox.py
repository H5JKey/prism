from datetime import datetime
from typing import Any

import pytest
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.constants import TOPIC_MAX_LENGTH
from infrastructure.database.models import Outbox
from tests.helpers import assert_sqlstate_code, SQLState


async def create_outbox(session: AsyncSession, **kwargs: Any) -> Outbox:
    outbox_data = {
        "topic": "test_topic",
        "message": {
            "field1": "value1",
            "field2": "value2",
        },
        "event_date": datetime(year=2025, month=1, day=1),
        "status": "pending",
    }
    outbox = Outbox(**outbox_data)
    for field, value in kwargs.items():
        setattr(outbox, field, value)

    session.add(outbox)
    await session.flush()
    return outbox


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
