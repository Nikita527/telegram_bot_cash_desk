"""Add strig for check

Revision ID: 5b5c6492bd58
Revises: 592744de9d09
Create Date: 2024-06-25 18:40:19.942180

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5b5c6492bd58"
down_revision: Union[str, None] = "592744de9d09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
