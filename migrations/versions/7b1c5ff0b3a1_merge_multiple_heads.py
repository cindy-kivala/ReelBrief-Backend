"""Merge multiple heads

Revision ID: 7b1c5ff0b3a1
Revises: 20fda94dffa4, 7bdf894e9e6c
Create Date: 2025-10-29 17:24:44.022880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b1c5ff0b3a1'
down_revision = ('20fda94dffa4', '7bdf894e9e6c')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
