"""create scrims table

Revision ID: create_scrims_table
Revises: add_approval_channel
Create Date: 2025-05-14 13:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_scrims_table'
down_revision = 'add_approval_channel'
branch_labels = None
depends_on = None


def upgrade():
    # Create scrims table
    op.create_table(
        'scrims',
        sa.Column('scrim_id', sa.Integer(), primary_key=True),
        sa.Column('creator_id', sa.BigInteger(), nullable=False),
        sa.Column('creator_team_id', sa.Integer(), sa.ForeignKey('teams.team_id'), nullable=True),
        sa.Column('scrim_type', sa.String(20), nullable=False),
        sa.Column('server_code', sa.String(50), nullable=True),
        sa.Column('scheduled_time', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), server_default='open'),
        sa.Column('message_id', sa.BigInteger(), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), nullable=True),
        sa.Column('team_size', sa.Integer(), server_default='5'),
        sa.Column('opponent_id', sa.BigInteger(), nullable=True),
        sa.Column('opponent_team_id', sa.Integer(), sa.ForeignKey('teams.team_id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('matched_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
    )


def downgrade():
    # Drop scrims table
    op.drop_table('scrims')
