# -*- encoding: utf-8 -*-
from sqlalchemy import func
from apps import db


class YTLogs(db.Model):
    __tablename__ = 'YT_Logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_module = db.Column(db.String(24), nullable=False)
    text = db.Column(db.String(2048), nullable=False)
    user_uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)


class Playlist(db.Model):
    __tablename__ = 'YT_Playlist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(48), nullable=False)
    last_used = db.Column(db.DateTime, default=func.now())
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)


class CreatorPlaylist(db.Model):
    __tablename__ = 'YT_CreatorPlaylist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creator_name = db.Column(db.String(48), nullable=False)
    playlist_name = db.Column(db.String(48), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    user_uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)


class Tag(db.Model):
    __tablename__ = 'YT_Tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    user_uuid = db.Column(db.String(36), nullable=False)
    group = db.Column(db.String(36), nullable=True)
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
    playlist_uuid = db.Column(db.String(36))
    v = db.Column(db.Boolean, default=False, nullable=False)
    uuid = db.Column(db.String(36), nullable=False)


class ApiExchange(db.Model):
    __tablename__ = 'ApiExchange'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    module = db.Column(db.String(20), nullable=False)
    command = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, default=func.now())
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)

