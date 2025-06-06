"""empty message

Revision ID: 1837486a3a97
Revises: 1a34571fbb45
Create Date: 2025-05-12 17:39:09.039436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1837486a3a97'
down_revision: Union[str, None] = '1a34571fbb45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('team_members', sa.Column('rating', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('team_members', 'rating')
    # ### end Alembic commands ###
