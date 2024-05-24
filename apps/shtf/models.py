# -*- encoding: utf-8 -*-
from sqlalchemy import func
from apps import db


class Task(db.Model):
    __tablename__ = 'TD_Task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    tick_id = db.Column(db.String(26), nullable=True)
    created = db.Column(db.DateTime, default=func.now())
    modified = db.Column(db.DateTime, default=func.now())
    start_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.SmallInteger, default=1)
    status = db.Column(db.SmallInteger, default=0)
    project = db.Column(db.String(36), nullable=True)
    tick_project_id = db.Column(db.String(26), nullable=True)
    uuid = db.Column(db.String(36), nullable=False)
    tags = db.Column(db.Text, nullable=True)
    contexts = db.Column(db.Text, nullable=True)


class Project(db.Model):
    __tablename__ = 'TD_Project'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    tick_project_id = db.Column(db.String(26), nullable=True)
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


class Physical(db.Model):
    __tablename__ = 'SHTF_Physical'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    amount = db.Column(db.Integer, default=0, nullable=False)
    activity_uuid = db.Column(db.String(32), nullable=False)
    calculated_pts = db.Column(db.Integer, default=1, nullable=False)
    calculated_health = db.Column(db.Integer, default=1, nullable=False)


class Activity(db.Model):
    __tablename__ = 'SHTF_Activity'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    name = db.Column(db.String(32), nullable=False)
    basic_pts_ratio = db.Column(db.Float, nullable=False, default=1.0)
    added_pts_ratio = db.Column(db.Float, nullable=True, default=1.0)
    basic_health_ratio = db.Column(db.Float, nullable=False, default=1.0)
    added_health_ratio = db.Column(db.Float, nullable=True, default=1.0)


class Resources(db.Model):
    __tablename__ = 'SHTF_Resources'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    name = db.Column(db.String(32), nullable=False)
    owned = db.Column(db.Boolean, default=False)
    amount = db.Column(db.Integer, default=0, nullable=False)
    weight = db.Column(db.Float, nullable=False, default=1.0)
    added_pts_ratio = db.Column(db.Float, nullable=True, default=1.0)
    added_health_ratio = db.Column(db.Float, nullable=True, default=1.0)


class BodyWeight(db.Model):
    __tablename__ = 'SHTF_BodyWeight'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_uuid = db.Column(db.String(36), nullable=False)
    uuid = db.Column(db.String(36), nullable=False)
    modified = db.Column(db.DateTime, default=func.now())
    weight = db.Column(db.Float, nullable=False, default=1.0)
