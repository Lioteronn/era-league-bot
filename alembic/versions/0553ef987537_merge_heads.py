"""merge heads

Revision ID: 0553ef987537
Revises: 3acfe1f277d3, add_invitation_system
Create Date: 2025-05-12 16:30:45.515079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0553ef987537'
down_revision: Union[str, None] = ('3acfe1f277d3', 'add_invitation_system')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
