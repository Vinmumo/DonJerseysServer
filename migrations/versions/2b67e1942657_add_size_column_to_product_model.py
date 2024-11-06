"""Add size column to Product model

Revision ID: 2b67e1942657
Revises: e8fdaa9e2bd5
Create Date: 2024-11-06 11:15:30.404307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b67e1942657'
down_revision = 'e8fdaa9e2bd5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('size', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('size')

    # ### end Alembic commands ###
