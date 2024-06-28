"""Add strig for check

Revision ID: 592744de9d09
Revises: c1b561b5f9d5
Create Date: 2024-06-25 18:38:18.516980

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "592744de9d09"
down_revision: Union[str, None] = "c1b561b5f9d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
