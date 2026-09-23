from typing import Any

from infrastructure.database.models import Project, Tag
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_infrastructure.test_database.test_models.factories import (
    create_file,
    create_project,
    create_render,
    create_tag,
    create_user,
)


async def create_default_project(session: AsyncSession, **kwargs: Any) -> Project:
    user = await create_user(session)
    source_file = await create_file(session)
    render = await create_render(session, file=source_file)
    project = await create_project(
        session,
        user=user,
        source_file=source_file,
        render=render,
        **kwargs,
    )
    return project


async def create_default_tag(session: AsyncSession, **kwargs: Any) -> Tag:
    source_file = await create_file(session)
    render = await create_render(session)
    user = await create_user(session)
    project = await create_project(
        session,
        user=user,
        source_file=source_file,
        render=render,
    )
    tag = await create_tag(session, project=project, **kwargs)
    return tag
