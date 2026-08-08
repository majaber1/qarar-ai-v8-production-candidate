"""add clarification gate columns

Revision ID: 7e36fbd7e306
Revises: 21cbfdcab740
Create Date: 2026-08-08 00:55:57.288657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e36fbd7e306'
down_revision: Union[str, Sequence[str], None] = '21cbfdcab740'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('decision_cases', sa.Column('pending_clarifications', sa.JSON(), nullable=True))
    op.add_column('decision_cases', sa.Column('clarification_answers', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('decision_cases', 'clarification_answers')
    op.drop_column('decision_cases', 'pending_clarifications')
