"""Add users table

Revision ID: 351101ffa59f
Revises: 
Create Date: 2020-05-22 18:39:36.471873

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '351101ffa59f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'Users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Users')
    # ### end Alembic commands ###
