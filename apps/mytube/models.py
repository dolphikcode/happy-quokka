# -*- encoding: utf-8 -*-
from sqlalchemy import func
from apps import db


class Playlist(db.Model):
    __tablename__ = 'YT_Playlist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(48), nullable=False)
    last_used = db.Column(db.DateTime, default=func.now())
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)


class PlaylistVideo(db.Model):
    __tablename__ = 'YT_PlaylistVideo'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    playlist_uuid = db.Column(db.String(36), nullable=False)
    video_uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)
    status = db.Column(db.Boolean, default=False)


class CreatorPlaylist(db.Model):
    __tablename__ = 'YT_CreatorPlaylist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creator_name = db.Column(db.String(48), nullable=False)
    playlist_name = db.Column(db.String(48), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    user_uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)


class TagVideo(db.Model):
    __tablename__ = 'YT_TagVideo'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    tag_uuid = db.Column(db.String(36), nullable=False)
    video_uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)
    status = db.Column(db.Boolean, default=False)


class Video(db.Model):
    __tablename__ = 'YT_Video'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    youtube_id = db.Column(db.String(12), nullable=False)
    video_position = db.Column(db.Float, default=0)
    user_uuid = db.Column(db.String(36), nullable=False)
    title = db.Column(db.String(512), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    channel = db.Column(db.String(100), nullable=True)
    channel_url = db.Column(db.String(256), nullable=True)
    # thumbnail = db.Column(db.LargeBinary(length=(2 ** 32) - 1), nullable=True)
    duration = db.Column(db.Integer)
    watched = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    to_download = db.Column(db.Boolean, default=False)
    release_date = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=func.now())
    modified = db.Column(db.DateTime, default=func.now())
    last_visited = db.Column(db.DateTime)
    comment = db.Column(db.Text)
    rate = db.Column(db.Integer)
    chapters = db.Column(db.Text, nullable=True)
    v = db.Column(db.Boolean, default=False, nullable=False)
    uuid = db.Column(db.String(36), nullable=False)


class LoadMore(db.Model):
    __tablename__ = 'YT_LoadMore'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    data = db.Column(db.Text, nullable=True)


class VideoToProcess(db.Model):
    __tablename__ = 'YT_VideoToProcess'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    youtube_id = db.Column(db.String(12), nullable=False)
    user_uuid = db.Column(db.String(36), nullable=False)
    uuid = db.Column(db.String(36), nullable=False)
    status = db.Column(db.SmallInteger, default=0)
