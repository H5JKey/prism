"""remove project optional description constraint

Revision ID: da1780a42a65
Revises: 11f4a9085334
Create Date: 2026-09-22 19:08:21.051420

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "da1780a42a65"
down_revision: Union[str, Sequence[str], None] = "11f4a9085334"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        ALTER TABLE projects
        ALTER COLUMN description SET NOT NULL
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE projects
        ALTER COLUMN description DROP NOT NULL
        """
    )
