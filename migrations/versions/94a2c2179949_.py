"""empty message

Revision ID: 94a2c2179949
Revises: 761fa883198c
Create Date: 2024-01-11 12:02:20.983821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94a2c2179949'
down_revision = '761fa883198c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('YT_Video', sa.Column('v', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('YT_Video', 'v')
    # ### end Alembic commands ###
