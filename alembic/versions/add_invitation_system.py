"""
Add invitation system tables and update server config

Revision ID: add_invitation_system
Revises: f511222c40f9
Create Date: 2025-05-12 16:35:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_invitation_system'
down_revision = 'f511222c40f9'
branch_labels = None
depends_on = None


def upgrade():
    # Add team_invite_approval_channel_id to server_config table
    op.add_column('server_config', sa.Column('team_invite_approval_channel_id', sa.BigInteger(), nullable=True))
    
    # Create invitations table
    op.create_table('invitations',
        sa.Column('invitation_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('inviter_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'accepted', 'declined', 'expired', name='invitationstatus'), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.team_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['inviter_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('invitation_id')
    )


def downgrade():
    # Drop invitations table
    op.drop_table('invitations')
    
    # Remove team_invite_approval_channel_id from server_config table
    op.drop_column('server_config', 'team_invite_approval_channel_id')
