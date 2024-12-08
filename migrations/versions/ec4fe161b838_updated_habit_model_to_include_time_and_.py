"""Updated habit model to include time and alert

Revision ID: ec4fe161b838
Revises: 5e6fa3eaff70
Create Date: 2024-12-08 07:51:58.416462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec4fe161b838'
down_revision = '5e6fa3eaff70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('habit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('time', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('alert', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('habit', schema=None) as batch_op:
        batch_op.drop_column('alert')
        batch_op.drop_column('time')

    # ### end Alembic commands ###
