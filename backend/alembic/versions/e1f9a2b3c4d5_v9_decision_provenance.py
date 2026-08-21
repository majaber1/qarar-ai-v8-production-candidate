"""Decision provenance, user-defined options, and score override history.

Revision ID: e1f9a2b3c4d5
Revises: d83a1f0c9200
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e1f9a2b3c4d5'
down_revision: Union[str, None] = 'd83a1f0c9200'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('decision_cases') as batch:
        batch.add_column(sa.Column('options', sa.JSON(), nullable=True))
        batch.add_column(sa.Column('score_provenance', sa.JSON(), nullable=True))
        batch.add_column(sa.Column('override_history', sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('decision_cases') as batch:
        batch.drop_column('override_history')
        batch.drop_column('score_provenance')
        batch.drop_column('options')
