"""add_project_approval_workflow_fields

Revision ID: 9b449846d4a2
Revises: 87104d5e146f
Create Date: 2025-11-02 20:32:42.547099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b449846d4a2'
down_revision = '87104d5e146f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('projects', sa.Column('approved_at', sa.DateTime(), nullable=True))
    op.add_column('projects', sa.Column('approved_by', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('assignment_requested', sa.Boolean(), server_default='false'))
    op.add_column('projects', sa.Column('assigned_at', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_projects_approved_by', 'projects', 'users', ['approved_by'], ['id'])

def downgrade():
    op.drop_constraint('fk_projects_approved_by', 'projects', type_='foreignkey')
    op.drop_column('projects', 'assigned_at')
    op.drop_column('projects', 'assignment_requested')
    op.drop_column('projects', 'rejection_reason')
    op.drop_column('projects', 'approved_by')
    op.drop_column('projects', 'approved_at')
