"""add tag cascade on delete project_id

Revision ID: 11f4a9085334
Revises: 2954f180ab5b
Create Date: 2026-09-22 18:27:00.235011

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "11f4a9085334"
down_revision: Union[str, Sequence[str], None] = "2954f180ab5b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        ALTER TABLE tags
        DROP CONSTRAINT fk_tags_project_id_projects,
        ADD CONSTRAINT fk_tags_project_id_projects 
        FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE tags
        DROP CONSTRAINT fk_tags_project_id_projects,
        ADD CONSTRAINT fk_tags_project_id_projects 
        FOREIGN KEY (project_id) REFERENCES projects (id)
        """
    )
