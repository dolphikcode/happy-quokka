"""empty message

Revision ID: 485489777ba2
Revises: 67540079d4af
Create Date: 2024-01-07 18:41:01.191189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '485489777ba2'
down_revision = '67540079d4af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Users', sa.Column('modified', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Users', 'modified')
    # ### end Alembic commands ###
