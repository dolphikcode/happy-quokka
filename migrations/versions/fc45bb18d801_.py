"""empty message

Revision ID: fc45bb18d801
Revises: 94ccec8a47b0
Create Date: 2024-04-15 11:40:00.526701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc45bb18d801'
down_revision = '94ccec8a47b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('POD_Chapters', schema=None) as batch_op:
        batch_op.add_column(sa.Column('addict_podcast_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('addict_episode_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('custom_bookmark', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('update_date', sa.BigInteger(), nullable=True))
        batch_op.drop_column('addict_podcastId')
        batch_op.drop_column('addict_episodeId')
        batch_op.drop_column('updateDate')
        batch_op.drop_column('customBookmark')

    with op.batch_alter_table('POD_Episodes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('playback_date', sa.BigInteger(), nullable=True))
        batch_op.drop_column('playbackDate')

    with op.batch_alter_table('POD_Podcasts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('latest_publication_date', sa.BigInteger(), nullable=False))
        batch_op.drop_column('last_modified')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('POD_Podcasts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('last_modified', sa.BIGINT(), autoincrement=False, nullable=False))
        batch_op.drop_column('latest_publication_date')

    with op.batch_alter_table('POD_Episodes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('playbackDate', sa.BIGINT(), autoincrement=False, nullable=False))
        batch_op.drop_column('playback_date')

    with op.batch_alter_table('POD_Chapters', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customBookmark', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('updateDate', sa.BIGINT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('addict_episodeId', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('addict_podcastId', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_column('update_date')
        batch_op.drop_column('custom_bookmark')
        batch_op.drop_column('addict_episode_id')
        batch_op.drop_column('addict_podcast_id')

    # ### end Alembic commands ###
