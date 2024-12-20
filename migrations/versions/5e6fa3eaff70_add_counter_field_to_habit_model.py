"""Add counter field to Habit model

Revision ID: 5e6fa3eaff70
Revises: 
Create Date: 2024-12-07 22:44:25.386087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e6fa3eaff70'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('habit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('counter', sa.Integer(), nullable=True))
        batch_op.alter_column('interval',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=150),
               existing_nullable=False)
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('habit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DATETIME(), nullable=True))
        batch_op.alter_column('interval',
               existing_type=sa.String(length=150),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
        batch_op.drop_column('counter')

    # ### end Alembic commands ###
