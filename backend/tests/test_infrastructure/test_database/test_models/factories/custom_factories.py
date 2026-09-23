from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.models import File, Outbox, Render, User, Project, Tag


async def create_file(session: AsyncSession, **kwargs: Any) -> File:
    file_data = {
        "name": "file_name",
        "size": 1000,
        "bucket": "test_bucket",
        "key": "test_key",
    }
    file = File(**file_data)
    for field, value in kwargs.items():
        setattr(file, field, value)

    session.add(file)
    await session.flush()
    return file


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


async def create_render(
    session: AsyncSession,
    file: File | None = None,
    **kwargs: Any,
) -> Render:
    file_id = file.id if file else None
    render_data = {
        "width": 1000,
        "height": 1000,
        "samples": 100,
        "denoiser": True,
        "gpu": True,
        "file_id": file_id,
    }
    render = Render(**render_data)
    for field, value in kwargs.items():
        setattr(render, field, value)

    session.add(render)
    await session.flush()
    return render


async def create_user(session: AsyncSession, **kwargs: Any) -> User:
    user_data = {
        "surname": "surname",
        "name": "name",
        "username": "username",
        "email": "email@mail.com",
        "encrypted_password": "encrypted_password",
        "registration_date": datetime(year=2025, month=12, day=31),
    }

    user = User(**user_data)
    for field, value in kwargs.items():
        setattr(user, field, value)

    session.add(user)
    await session.flush()
    return user


async def create_project(
    session: AsyncSession,
    user: User,
    source_file: File,
    render: Render,
    **kwargs: Any,
) -> Project:
    project_data = {
        "name": "project_name",
        "description": "description",
        "create_date": datetime(year=2025, month=1, day=1),
        "status": "rendering",
        "visibility": "public",
        "user_id": user.id,
        "source_file_id": source_file.id,
        "render_id": render.id,
    }

    project = Project(**project_data)
    for field, value in kwargs.items():
        setattr(project, field, value)

    session.add(project)
    await session.flush()
    return project


async def create_tag(
    session: AsyncSession,
    project: Project | None = None,
    **kwargs: Any,
) -> Tag:
    tag_data = {
        "name": "tag_name",
        "project_id": project.id,
    }

    tag = Tag(**tag_data)
    for field, value in kwargs.items():
        setattr(tag, field, value)

    session.add(tag)
    await session.flush()
    return tag
