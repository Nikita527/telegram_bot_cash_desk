"""Add strig for check

Revision ID: 4f1855124d3d
Revises: 8808e58d6024
Create Date: 2024-06-25 18:47:49.256161

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4f1855124d3d"
down_revision: Union[str, None] = "8808e58d6024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
