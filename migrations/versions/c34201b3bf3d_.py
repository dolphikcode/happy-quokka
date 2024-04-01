"""empty message

Revision ID: c34201b3bf3d
Revises: 4d3a428b2d23
Create Date: 2024-04-01 10:51:25.131658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c34201b3bf3d'
down_revision = '4d3a428b2d23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('TD_Project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tick_project_id', sa.String(length=26), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('TD_Project', schema=None) as batch_op:
        batch_op.drop_column('tick_project_id')

    # ### end Alembic commands ###
