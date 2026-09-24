from core.constants import EventStatus
from infrastructure.database.repositories import OutboxRepository
from schemas.event import EventCreate
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_infrastructure.test_database.test_models.factories import create_outbox


class TestOutboxRepository:
    async def test_get_by_id(
        self,
        session: AsyncSession,
        outbox_repository: OutboxRepository,
    ) -> None:
        event = await create_outbox(session)
        session.expunge(event)
        selected_event = await outbox_repository.get_by_id(event.id)
        assert selected_event.id == event.id
        assert selected_event.topic == event.topic
        assert selected_event.message == event.message
        assert selected_event.status == event.status
        assert selected_event.event_date == event.event_date

    async def test_get_not_exist_event_by_id(
        self,
        outbox_repository: OutboxRepository,
    ) -> None:
        selected_event = await outbox_repository.get_by_id(-1)
        assert selected_event is None

    async def test_create_event(
        self,
        session: AsyncSession,
        outbox_repository: OutboxRepository,
    ) -> None:
        create_event_data = EventCreate(
            topic="topic",
            message={
                "field1": "value1",
                "field2": "value2",
            },
        )
        created_event = await outbox_repository.create_event(create_event_data)
        session.expunge(created_event)
        selected_event = await outbox_repository.get_by_id(created_event.id)
        assert selected_event is not None
        assert selected_event.topic == create_event_data.topic
        assert selected_event.message == create_event_data.message
        assert selected_event.status == EventStatus.pending
        assert selected_event.event_date is not None

    async def test_mark_event_as_sent(
        self,
        session: AsyncSession,
        outbox_repository: OutboxRepository,
    ) -> None:
        event = await create_outbox(session)
        await outbox_repository.mark_event_as_sent(event.id)
        selected_event = await outbox_repository.get_by_id(event.id)
        assert selected_event is not None
        assert selected_event.topic == event.topic
        assert selected_event.message == event.message
        assert selected_event.status == EventStatus.sent
        assert selected_event.event_date is not None

    async def test_get_pending_event(
        self,
        session: AsyncSession,
        outbox_repository: OutboxRepository,
    ) -> None:
        event = await create_outbox(session)
        selected_event = await outbox_repository.get_pending_event()
        assert selected_event is not None
        assert selected_event.topic == event.topic
        assert selected_event.message == event.message
        assert selected_event.status == EventStatus.pending
        assert selected_event.event_date is not None

    async def test_get_pending_not_exist_event(
        self,
        outbox_repository: OutboxRepository,
    ) -> None:
        selected_event = await outbox_repository.get_pending_event()
        assert selected_event is None
