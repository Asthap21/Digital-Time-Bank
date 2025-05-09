"""Initial migration

Revision ID: 0372ee5d221e
Revises: 
Create Date: 2025-05-03 13:34:01.771574

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0372ee5d221e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('service', schema=None) as batch_op:
        batch_op.add_column(sa.Column('available', sa.Boolean(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mobile', sa.String(length=15), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('mobile')

    with op.batch_alter_table('service', schema=None) as batch_op:
        batch_op.drop_column('available')

    # ### end Alembic commands ###
