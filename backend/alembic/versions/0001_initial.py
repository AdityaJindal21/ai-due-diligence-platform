"""initial migration

Revision ID: 0001_initial
Revises: 
Create Date: 2026-06-29
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # create tables using metadata for a simple initial migration
    from app.db.models import Base
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade():
    from app.db.models import Base
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
