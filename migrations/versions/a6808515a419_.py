"""empty message

Revision ID: a6808515a419
Revises: 08024916a992
Create Date: 2024-02-22 10:45:58.017111

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a6808515a419'
down_revision = '08024916a992'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('YT_Tag')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('YT_Tag',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"YT_Tag_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=32), autoincrement=False, nullable=False),
    sa.Column('user_uuid', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('uuid', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('group', sa.VARCHAR(length=36), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='YT_Tag_pkey')
    )
    # ### end Alembic commands ###
