"""
Add approval channel to server config

Revision ID: add_approval_channel
Revises: 0553ef987537
Create Date: 2025-05-12 16:40:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_approval_channel'
down_revision = '0553ef987537'  # This is the merge revision
branch_labels = None
depends_on = None


def upgrade():
    # Add team_invite_approval_channel_id to server_config table
    op.add_column('server_config', sa.Column('team_invite_approval_channel_id', sa.BigInteger(), nullable=True))


def downgrade():
    # Remove team_invite_approval_channel_id from server_config table
    op.drop_column('server_config', 'team_invite_approval_channel_id')
