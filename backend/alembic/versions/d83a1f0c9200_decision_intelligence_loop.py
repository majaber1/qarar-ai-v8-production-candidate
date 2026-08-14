"""Decision intelligence lifecycle, actions, outcomes, and evidence versions.

Revision ID: d83a1f0c9200
Revises: f25b9a107e31
"""
from alembic import op
import sqlalchemy as sa

revision='d83a1f0c9200';down_revision='f25b9a107e31';branch_labels=None;depends_on=None

def upgrade():
    with op.batch_alter_table('decision_cases') as batch:
        batch.add_column(sa.Column('scoring_criteria',sa.JSON(),nullable=True))
        batch.add_column(sa.Column('calculation_metadata',sa.JSON(),nullable=True))
    op.create_table('decision_actions_v83',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('tenant_id',sa.String(80),nullable=False),sa.Column('case_id',sa.Integer(),nullable=False),sa.Column('title',sa.String(250),nullable=False),sa.Column('description',sa.Text()),sa.Column('owner',sa.String(200),nullable=False),sa.Column('status',sa.String(30),nullable=False),sa.Column('priority',sa.String(20),nullable=False),sa.Column('due_date',sa.Date()),sa.Column('dependency_id',sa.Integer()),sa.Column('created_by',sa.String(200),nullable=False),sa.Column('source_reference',sa.String(500)),sa.Column('completion_date',sa.Date()),sa.Column('notes',sa.Text()),sa.Column('created_at',sa.DateTime(),nullable=False),sa.Column('updated_at',sa.DateTime(),nullable=False))
    op.create_table('decision_outcomes_v83',sa.Column('id',sa.Integer(),primary_key=True),sa.Column('tenant_id',sa.String(80),nullable=False),sa.Column('case_id',sa.Integer(),nullable=False),sa.Column('result',sa.String(20),nullable=False),sa.Column('expected_result',sa.Text(),nullable=False),sa.Column('actual_result',sa.Text(),nullable=False),sa.Column('lessons_learned',sa.Text()),sa.Column('corrective_action',sa.Text()),sa.Column('next_review_date',sa.Date()),sa.Column('recorded_by',sa.String(200),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False))
    for name in ('tenant_id','case_id','status','priority','owner','due_date','dependency_id'):op.create_index(f'ix_decision_actions_v83_{name}','decision_actions_v83',[name])
    for name in ('tenant_id','case_id','result','next_review_date'):op.create_index(f'ix_decision_outcomes_v83_{name}','decision_outcomes_v83',[name])
    with op.batch_alter_table('knowledge_sources_v5') as batch:
        batch.add_column(sa.Column('version',sa.Integer(),nullable=False,server_default='1'));batch.add_column(sa.Column('source_owner',sa.String(200)));batch.add_column(sa.Column('reviewed_at',sa.DateTime()));batch.add_column(sa.Column('supersedes_id',sa.Integer()));batch.add_column(sa.Column('deleted_at',sa.DateTime()))
        batch.create_index('ix_knowledge_sources_v5_supersedes_id',['supersedes_id']);batch.create_index('ix_knowledge_sources_v5_deleted_at',['deleted_at'])

def downgrade():
    with op.batch_alter_table('knowledge_sources_v5') as batch:
        batch.drop_index('ix_knowledge_sources_v5_deleted_at');batch.drop_index('ix_knowledge_sources_v5_supersedes_id')
        for name in ('deleted_at','supersedes_id','reviewed_at','source_owner','version'):batch.drop_column(name)
    op.drop_table('decision_outcomes_v83');op.drop_table('decision_actions_v83')
    with op.batch_alter_table('decision_cases') as batch:batch.drop_column('calculation_metadata');batch.drop_column('scoring_criteria')
