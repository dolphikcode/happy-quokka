# -*- encoding: utf-8 -*-
from sqlalchemy import func
from apps import db


class Task(db.Model):
    __tablename__ = 'TD_Task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    created = db.Column(db.DateTime, default=func.now())
    modified = db.Column(db.DateTime, default=func.now())
    date_due = db.Column(db.Date, nullable=True)
    time_due = db.Column(db.Time, nullable=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.SmallInteger, default=1)
    status = db.Column(db.SmallInteger, default=0)
    project = db.Column(db.String(36), nullable=True)
    uuid = db.Column(db.String(36), nullable=False)
    tags = db.Column(db.Text, nullable=True)
    contexts = db.Column(db.Text, nullable=True)


class Project(db.Model):
    __tablename__ = 'TD_Project'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    created = db.Column(db.DateTime, default=func.now())
    modified = db.Column(db.DateTime, default=func.now())
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.SmallInteger, default=0)
    subproject_of = db.Column(db.String(36), nullable=True)
    uuid = db.Column(db.String(36), nullable=False)
    color = db.Column(db.String(6), nullable=True)
    icon = db.Column(db.String(36), nullable=True)


class Context(db.Model):
    __tablename__ = 'TD_Context'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    user_uuid = db.Column(db.String(36), nullable=False)
    group = db.Column(db.String(36), nullable=True)
    modified = db.Column(db.DateTime, default=func.now())
    uuid = db.Column(db.String(36), nullable=False)
