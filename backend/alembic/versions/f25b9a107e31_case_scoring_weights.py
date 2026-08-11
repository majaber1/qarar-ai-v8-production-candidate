"""Add per-case scoring weights.

Revision ID: f25b9a107e31
Revises: c9b7e4a812f0
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f25b9a107e31'
down_revision: Union[str, None] = 'c9b7e4a812f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('decision_cases') as batch:
        batch.add_column(sa.Column('scoring_weights', sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('decision_cases') as batch:
        batch.drop_column('scoring_weights')
