"""Merge heads

Revision ID: 3746880c5c0a
Revises: e8724733169b, ea22d4bc3a12
Create Date: 2024-05-21 20:01:07.264112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3746880c5c0a'
down_revision: Union[str, None] = ('e8724733169b', 'ea22d4bc3a12')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
