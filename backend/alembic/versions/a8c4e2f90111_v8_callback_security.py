"""V8 signed callback replay protection.

Revision ID: a8c4e2f90111
Revises: 7e36fbd7e306
"""
from alembic import op
import sqlalchemy as sa

revision = 'a8c4e2f90111'
down_revision = '7e36fbd7e306'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('automation_callback_receipts_v8',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('nonce', sa.String(length=128), nullable=False),
        sa.Column('received_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('nonce', name='uq_automation_callback_nonce_v8'))
    op.create_index('ix_automation_callback_receipts_v8_run_id','automation_callback_receipts_v8',['run_id'])
    op.create_index('ix_automation_callback_receipts_v8_received_at','automation_callback_receipts_v8',['received_at'])

def downgrade():
    op.drop_index('ix_automation_callback_receipts_v8_received_at', table_name='automation_callback_receipts_v8')
    op.drop_index('ix_automation_callback_receipts_v8_run_id', table_name='automation_callback_receipts_v8')
    op.drop_table('automation_callback_receipts_v8')
