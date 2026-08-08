"""V8 workspaces, project-scoped evidence, and user access requests.

Revision ID: c9b7e4a812f0
Revises: a8c4e2f90111
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c9b7e4a812f0'
down_revision: Union[str, None] = 'a8c4e2f90111'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('projects_v8',
        sa.Column('id', sa.Integer(), primary_key=True), sa.Column('tenant_id', sa.String(80), nullable=False),
        sa.Column('name', sa.String(250), nullable=False), sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('owner', sa.String(200), nullable=False), sa.Column('status', sa.String(30), nullable=False),
        sa.Column('created_by', sa.String(200), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_index('ix_projects_v8_tenant_id', 'projects_v8', ['tenant_id'])
    op.create_index('ix_projects_v8_status', 'projects_v8', ['status'])
    op.create_table('workspace_users_v8',
        sa.Column('id', sa.Integer(), primary_key=True), sa.Column('tenant_id', sa.String(80), nullable=False),
        sa.Column('email', sa.String(320), nullable=False), sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('organization', sa.String(250), nullable=False), sa.Column('password_hash', sa.String(500), nullable=False),
        sa.Column('role', sa.String(40), nullable=False), sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('tenant_id', 'email', name='uq_workspace_user_tenant_email_v8'))
    op.create_index('ix_workspace_users_v8_tenant_id', 'workspace_users_v8', ['tenant_id'])
    op.create_index('ix_workspace_users_v8_email', 'workspace_users_v8', ['email'])
    op.create_index('ix_workspace_users_v8_active', 'workspace_users_v8', ['active'])
    op.create_table('access_requests_v8',
        sa.Column('id', sa.Integer(), primary_key=True), sa.Column('tenant_id', sa.String(80), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False), sa.Column('requested_role', sa.String(40), nullable=False),
        sa.Column('status', sa.String(30), nullable=False), sa.Column('reviewed_by', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.create_index('ix_access_requests_v8_tenant_id', 'access_requests_v8', ['tenant_id'])
    op.create_index('ix_access_requests_v8_user_id', 'access_requests_v8', ['user_id'])
    op.create_index('ix_access_requests_v8_status', 'access_requests_v8', ['status'])
    op.create_table('user_sessions_v8',
        sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(64), nullable=False), sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('token_hash'))
    op.create_index('ix_user_sessions_v8_user_id', 'user_sessions_v8', ['user_id'])
    op.create_index('ix_user_sessions_v8_token_hash', 'user_sessions_v8', ['token_hash'], unique=True)
    op.create_index('ix_user_sessions_v8_expires_at', 'user_sessions_v8', ['expires_at'])
    op.create_index('ix_user_sessions_v8_revoked', 'user_sessions_v8', ['revoked'])
    with op.batch_alter_table('decision_cases') as batch:
        batch.add_column(sa.Column('project_id', sa.Integer(), nullable=True)); batch.create_index('ix_decision_cases_project_id', ['project_id'])
    with op.batch_alter_table('knowledge_sources_v5') as batch:
        batch.add_column(sa.Column('project_id', sa.Integer(), nullable=True)); batch.create_index('ix_knowledge_sources_v5_project_id', ['project_id'])
    with op.batch_alter_table('knowledge_chunks_v5') as batch:
        batch.add_column(sa.Column('project_id', sa.Integer(), nullable=True)); batch.create_index('ix_knowledge_chunks_v5_project_id', ['project_id'])
    with op.batch_alter_table('knowledge_items') as batch:
        batch.add_column(sa.Column('project_id', sa.Integer(), nullable=True)); batch.create_index('ix_knowledge_items_project_id', ['project_id'])


def downgrade() -> None:
    for table, index in [('knowledge_items','ix_knowledge_items_project_id'),('knowledge_chunks_v5','ix_knowledge_chunks_v5_project_id'),('knowledge_sources_v5','ix_knowledge_sources_v5_project_id'),('decision_cases','ix_decision_cases_project_id')]:
        with op.batch_alter_table(table) as batch:
            batch.drop_index(index); batch.drop_column('project_id')
    op.drop_table('user_sessions_v8'); op.drop_table('access_requests_v8'); op.drop_table('workspace_users_v8'); op.drop_table('projects_v8')
