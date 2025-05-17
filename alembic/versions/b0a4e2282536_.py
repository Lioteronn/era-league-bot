"""empty message

Revision ID: b0a4e2282536
Revises: 53d4a315969c, create_scrims_table
Create Date: 2025-05-14 14:08:20.040164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0a4e2282536'
down_revision: Union[str, None] = ('53d4a315969c', 'create_scrims_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
