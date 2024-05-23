# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from apps import db
from flask import render_template, request, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound

from apps.mytube.routes import get_playlists
from apps.home.models import *
from apps.mytube.models import Video
import re


@blueprint.route('/index')
@login_required
def index():
    return render_template('home/index.html',
                           segment='index',
                           playlists=get_playlists())


@blueprint.route('/logs')
@login_required
def logs():
    logs = db.session.scalars(
        db.select(Logs).filter_by(user_uuid=current_user.uuid)).all()

    processed_logs = []
    for l in logs:
        # Regular expression pattern to match the YouTube video ID
        pattern = r"ERROR: \[youtube\] ([\w-]+):"

        # Search for the pattern in the text
        match = re.search(pattern, l.text)
        video_id = ''
        vid = Video()
        action = ''

        # Extract and print the video ID if found
        if match:
            video_id = match.group(1)
            vid = db.session.scalars(
                db.select(Video).filter_by(user_uuid=current_user.uuid, youtube_id=video_id)).first()
            action = url_for('mytube_blueprint.video', video_uuid=vid.uuid)
            print("YouTube video ID:", video_id)
        else:
            print("No YouTube video ID found.")

        processed_log = {
            'id': l.id,
            'date': l.modified,
            'from_module': l.from_module,
            'text': l.text,
            'action': action
        }
        processed_logs.append(processed_log)

    return render_template('home/logs.html',
                           segment='logs',
                           logs=processed_logs)

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
