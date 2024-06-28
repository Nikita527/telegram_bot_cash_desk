"""Add telegram_id for User

Revision ID: 5ab86cdc725a
Revises: 4f1855124d3d
Create Date: 2024-06-26 17:34:05.004628

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5ab86cdc725a"
down_revision: Union[str, None] = "4f1855124d3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
