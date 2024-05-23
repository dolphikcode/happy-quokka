"""empty message

Revision ID: 033064702c77
Revises: fc45bb18d801
Create Date: 2024-05-23 09:45:50.647991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '033064702c77'
down_revision = 'fc45bb18d801'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('POD_Episodes', schema=None) as batch_op:
        batch_op.alter_column('duration',
               existing_type=sa.TEXT(),
               type_=sa.Integer(),
               nullable=False)
        batch_op.alter_column('playback_date',
               existing_type=sa.BIGINT(),
               nullable=False)

    with op.batch_alter_table('YT_Video', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_file_check', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('file_exist', sa.Boolean(), nullable=False, default=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('YT_Video', schema=None) as batch_op:
        batch_op.drop_column('file_exist')
        batch_op.drop_column('last_file_check')

    with op.batch_alter_table('POD_Episodes', schema=None) as batch_op:
        batch_op.alter_column('playback_date',
               existing_type=sa.BIGINT(),
               nullable=True)
        batch_op.alter_column('duration',
               existing_type=sa.Integer(),
               type_=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###
