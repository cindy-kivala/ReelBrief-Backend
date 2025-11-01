"""merge heads from Caleb's branch

Revision ID: d429134396ef
Revises: 20fda94dffa4, 8301a0867766
Create Date: 2025-10-30 02:27:58.061652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd429134396ef'
down_revision = ('20fda94dffa4', '8301a0867766')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
