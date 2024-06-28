"""Add strig for check

Revision ID: 8808e58d6024
Revises: 5b5c6492bd58
Create Date: 2024-06-25 18:47:12.087569

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8808e58d6024"
down_revision: Union[str, None] = "5b5c6492bd58"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
