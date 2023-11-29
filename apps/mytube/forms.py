# -*- encoding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class PlaylistForm(FlaskForm):
    name = StringField('Playlist Name',
                       id='playlist_name',
                       validators=[DataRequired()])
    submit = SubmitField('Create Playlist')
