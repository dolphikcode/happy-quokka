# -*- encoding: utf-8 -*-
from sqlalchemy import func
from apps import db


class Logs(db.Model):
    __tablename__ = 'Logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_module = db.Column(db.String(24), nullable=False)
    text = db.Column(db.String(2048), nullable=False)
    user_uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)


class Tag(db.Model):
    __tablename__ = 'Tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    user_uuid = db.Column(db.String(36), nullable=False)
    group = db.Column(db.String(36), nullable=True)
    modified = db.Column(db.DateTime, default=func.now())
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



