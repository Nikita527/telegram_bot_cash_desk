"""Add strig for check and payment_slip

Revision ID: c1b561b5f9d5
Revises: 10be82b0ec0e
Create Date: 2024-06-25 18:10:58.744781

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1b561b5f9d5"
down_revision: Union[str, None] = "10be82b0ec0e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
