"""add face fields to users

Revision ID: 3b1a2cface
Revises: 7390d0f6fc3d
Create Date: 2025-12-17

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3b1a2cface'
down_revision = '7390d0f6fc3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('face_image_path', sa.String(length=512), nullable=True))
        batch_op.add_column(sa.Column('face_hash', sa.String(length=128), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('face_hash')
        batch_op.drop_column('face_image_path')
