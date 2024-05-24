# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ActivityForm(FlaskForm):
    name = StringField('Activity Name',
                       id='activity_name',
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
