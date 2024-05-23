"""empty message

Revision ID: 39f770e4b26a
Revises: 1ed072c26da9
Create Date: 2024-04-10 14:10:27.938845

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39f770e4b26a'
down_revision = '1ed072c26da9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('POD_Chapters',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_uuid', sa.String(length=36), nullable=False),
    sa.Column('uuid', sa.String(length=36), nullable=False),
    sa.Column('addict_id', sa.Integer(), nullable=True),
    sa.Column('addict_podcastId', sa.Integer(), nullable=False),
    sa.Column('addict_episodeId', sa.Integer(), nullable=False),
    sa.Column('start', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('customBookmark', sa.Integer(), nullable=True),
    sa.Column('updateDate', sa.Integer(), nullable=True),
    sa.Column('isMuted', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('POD_Episodes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_uuid', sa.String(length=36), nullable=False),
    sa.Column('uuid', sa.String(length=36), nullable=False),
    sa.Column('addict_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('addict_podcast_id', sa.Integer(), nullable=False),
    sa.Column('guid', sa.Text(), nullable=False),
    sa.Column('url', sa.Text(), nullable=True),
    sa.Column('publication_date', sa.Integer(), nullable=False),
    sa.Column('creator', sa.Text(), nullable=True),
    sa.Column('short_description', sa.Text(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('download_url', sa.Text(), nullable=True),
    sa.Column('duration', sa.Text(), nullable=True),
    sa.Column('favorite', sa.Integer(), nullable=False),
    sa.Column('seen_status', sa.Integer(), nullable=False),
    sa.Column('new_status', sa.Integer(), nullable=False),
    sa.Column('position_to_resume', sa.Integer(), nullable=True),
    sa.Column('deleted_status', sa.Integer(), nullable=False),
    sa.Column('local_file_name', sa.Text(), nullable=True),
    sa.Column('thumbnail_id', sa.Integer(), nullable=True),
    sa.Column('is_artwork_extracted', sa.Integer(), nullable=True),
    sa.Column('playbackDate', sa.Integer(), nullable=False),
    sa.Column('chapters_extracted', sa.Integer(), nullable=True),
    sa.Column('transcript_url', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('POD_Podcasts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_uuid', sa.String(length=36), nullable=False),
    sa.Column('uuid', sa.String(length=36), nullable=False),
    sa.Column('addict_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('subscribed_status', sa.Integer(), nullable=False),
    sa.Column('homepage', sa.Text(), nullable=True),
    sa.Column('feed_url', sa.Text(), nullable=False),
    sa.Column('last_modified', sa.Integer(), nullable=False),
    sa.Column('author', sa.Text(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('folderName', sa.Text(), nullable=True),
    sa.Column('muted', sa.Integer(), nullable=True),
    sa.Column('topic_url', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('feed_url')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('POD_Podcasts')
    op.drop_table('POD_Episodes')
    op.drop_table('POD_Chapters')
    # ### end Alembic commands ###