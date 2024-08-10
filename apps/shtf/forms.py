# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.numeric import FloatField
from wtforms.validators import DataRequired


class ActivityForm(FlaskForm):
    name = StringField('Activity Name',
                       id='activity_name',
                       validators=[DataRequired()])
    basic_points_ratio = FloatField('Basic points ratio',
                       id='basic_points_ratio',
                       validators=[DataRequired()])
    basic_health_ratio = FloatField('Basic health ratio',
                       id='basic_health_ratio',
                       validators=[DataRequired()])
    submit = SubmitField('Create Activity')

#
# class TagForm(FlaskForm):
#     name = StringField('Tag Name',
#                        id='tag_name',
#                        validators=[DataRequired()])
#     group = StringField('Tag Group',
#                        id='tag_group')
#     submit = SubmitField('Create Tag')
