"""Add status to requests models

Revision ID: 10be82b0ec0e
Revises: 0dca10c0a99a
Create Date: 2024-06-25 16:38:30.902539

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "10be82b0ec0e"
down_revision: Union[str, None] = "0dca10c0a99a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
