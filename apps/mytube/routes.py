# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json

from sqlalchemy import func, desc

from apps.mytube import blueprint
from apps import db
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, current_app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from io import BytesIO
import os.path
from apps.mytube.models import *
import uuid


def prepare_videos(vids, arguments, title):
    # Create structure
    data = {}
    config = {}
    videos = []

    # Process each video
    video_folder = current_app.config['VIDEO_ROOT']

    for v in vids:
        # Check arguments
        if arguments.get('fw'):
            if v.watched != str2bool(arguments.get('fw')):
                continue
        if arguments.get('fd'):
            if v.to_download != str2bool(arguments.get('fd')):
                continue
        # Check if downloaded file exists
        file_found = False
        fname = os.path.join(video_folder, f'{json.loads(v.title)}.mp4')
        if (os.path.isfile(fname)):
            file_found = True
        if arguments.get('ff'):
            if file_found != str2bool(arguments.get('ff')):
                continue

        processed_video = {
            'id': v.id,
            'user_id': v.user_id,
            'title': json.loads(v.title),
            'url': v.url,
            'description': json.loads(v.description),
            'channel': v.channel,
            # channel_url - skip
            # thumbnail - reading from DB by loading page
            'duration': convert_seconds_to_hms(v.duration),
            'watched': v.watched,
            'deleted': v.deleted,
            'to_download': v.to_download,
            'file_exist': file_found,
            'release_date': convert_int_date_to_iso(v.release_date),
            'created': v.created,
            'modified': v.modified,
            'comment': v.comment,
            'rate': v.rate,
            'playlist_id': v.playlist_id,
            'playlist_name': get_playlist_name(v.playlist_id),
        }
        videos.append(processed_video)

    config = {
        'title': title,
        'count': len(videos),
        'fW': boolstr2number(arguments.get('fw')),
        'fD': boolstr2number(arguments.get('fd')),
        'fF': boolstr2number(arguments.get('ff')),
        'sort': sort2number(arguments.get('sort')),
        'trash': arguments.get('trash') if arguments.get('trash') else 'false'
    }

    data = {
        'config': config,
        'videos': videos,
    }
    return data


@blueprint.route('/')
@login_required
def mytube():
    arguments = request.args
    deleted = str2bool(arguments.get('trash')) if arguments.get('trash') else False
    segment = 'yt_trash' if arguments.get('trash') else 'mytube'
    # Sort videos
    column = 'created'
    order = 'asc'
    match arguments.get('sort'):
        case "-1":
            column = 'release_date'
            order = 'asc'
        case "-2":
            column = 'release_date'
            order = 'desc'
        case "0":
            column = 'created'
            order = 'asc'
        case "1":
            column = 'created'
            order = 'desc'
        case _:
            column = 'created'
            order = 'asc'
    videos = (db.session.scalars(db.select(Video)
                .filter_by(user_id=current_user.id)
                .filter_by(deleted=deleted)
                .order_by(getattr(Video, column).asc() if order == 'asc' else getattr(Video, column).desc()))
              .all())

    return render_template('mytube/mytube.html',
                           data=prepare_videos(videos, arguments, "All Videos"),
                           segment=segment,
                           playlists=get_playlists(),
                           )

    # return render_template('mytube/mytube.html',
    #                        title="All Videos",
    #                        segment='mytube',
    #                        count=len(videos),
    #                        videos=videos,
    #                        playlists=get_playlists(),
    #                        convert_seconds_to_hms=convert_seconds_to_hms,
    #                        convert_int_date_to_iso=convert_int_date_to_iso,
    #                        get_playlist_name=get_playlist_name)


@blueprint.route('/playlist/<int:playlist_id>')
@login_required
def mytube_playlist(playlist_id):
    arguments = request.args
    # Sort videos
    column = 'created'
    order = 'asc'
    match arguments.get('sort'):
        case "-1":
            column = 'release_date'
            order = 'asc'
        case "-2":
            column = 'release_date'
            order = 'desc'
        case "0":
            column = 'created'
            order = 'asc'
        case "1":
            column = 'created'
            order = 'desc'
        case _:
            column = 'created'
            order = 'asc'
    videos = (db.session.scalars(db.select(Video)
                .filter_by(user_id=current_user.id)
                .filter_by(playlist_id=playlist_id, deleted=False)
                .order_by(getattr(Video, column).asc() if order == 'asc' else getattr(Video, column).desc()))
              .all())

    playlist = db.session.get(Playlist, playlist_id)
    playlist.last_used = func.now()
    db.session.commit()

    return render_template('mytube/mytube.html',
                           data=prepare_videos(videos, arguments, playlist.name),
                           segment=playlist.name,
                           playlists=get_playlists(),
                           )
    # return render_template('mytube/mytube.html',
    #                        title=playlist.name,
    #                        segment=playlist.name,
    #                        videos=videos,
    #                        count=len(videos),
    #                        playlists=get_playlists(),
    #                        convert_seconds_to_hms=convert_seconds_to_hms,
    #                        convert_int_date_to_iso=convert_int_date_to_iso,
    #                        get_playlist_name=get_playlist_name)


# @blueprint.route('/trash')
# @login_required
# def mytube_trash():
#     arguments = request.args
#     # Sort videos
#     column = 'created'
#     order = 'asc'
#     match arguments.get('sort'):
#         case "-1":
#             column = 'release_date'
#             order = 'asc'
#         case "-2":
#             column = 'release_date'
#             order = 'desc'
#         case "0":
#             column = 'created'
#             order = 'asc'
#         case "1":
#             column = 'created'
#             order = 'desc'
#         case _:
#             column = 'created'
#             order = 'asc'
#     videos = (db.session.scalars(db.select(Video)
#                 .filter_by(user_id=current_user.id)
#                 .filter_by(deleted=True)
#                 .order_by(getattr(Video, column).asc() if order == 'asc' else getattr(Video, column).desc()))
#               .all())
#
#     return render_template('mytube/mytube.html',
#                            data=prepare_videos(videos, arguments, "Deleted Videos", 'yt_trash'),
#                            playlists=get_playlists(),
#                            )
    # return render_template('mytube/mytube.html',
    #                        title="Deleted Videos",
    #                        segment='yt_trash',
    #                        videos=videos,
    #                        count=len(videos),
    #                        playlists=get_playlists(),
    #                        convert_seconds_to_hms=convert_seconds_to_hms,
    #                        convert_int_date_to_iso=convert_int_date_to_iso,
    #                        get_playlist_name=get_playlist_name)


@blueprint.route('/video/<int:video_id>')
@login_required
def video(video_id):
    video = db.session.get(Video, video_id)
    chapters = db.session.scalars(db.select(Chapter).filter_by(movie_id=video_id)).all()

    # Check if video downloaded
    # json.loads(chapter.name)   !!!

    return render_template('mytube/video.html',
                           video=video,
                           chapters=chapters,
                           playlists=get_playlists(),
                           convert_seconds_to_hms=convert_seconds_to_hms,
                           segment='mytube')


@blueprint.route('/playlist/create', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if request.method == 'POST':
        new_playlist = Playlist(name=request.form['name'])
        db.session.add(new_playlist)
        db.session.commit()
        return redirect(url_for('all_videos'))
    return render_template('create_playlist.html')


@blueprint.route('/playlist/<int:playlist_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if request.method == 'POST':
        playlist.name = request.form['name']
        db.session.commit()
        return redirect(url_for('all_videos'))
    return render_template('edit_playlist.html', playlist=playlist)


def get_playlists():
    playlists = db.session.scalars(db.select(Playlist).order_by(desc(Playlist.last_used))).all()
    return playlists


def get_playlist_name(playlist_id):
    if playlist_id:
        playlist = Playlist.query.get(playlist_id)
        return playlist.name
    else:
        return ''


# Route to display video thumbnail
@blueprint.route('/video_thumbnail/<int:video_id>')
@login_required
def display_thumbnail(video_id):
    video = Video.query.get(video_id)

    if video and video.thumbnail:
        return send_file(BytesIO(video.thumbnail), mimetype='image/jpeg')
    else:
        # You can provide a default image or a placeholder if thumbnail is not available
        return send_file('path/to/default_thumbnail.jpg', mimetype='image/jpeg')


def convert_seconds_to_hms(seconds):
    # Use timedelta to format the duration
    duration = timedelta(seconds=seconds)

    # Extract hours, minutes, and seconds
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format the duration based on the presence of hours
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


# Function to convert integer date to ISO format
def convert_int_date_to_iso(int_date):
    date_str = str(int_date)
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:]
    iso_date = f"{year}-{month}-{day}"
    return iso_date


# Your other routes and functions...

# Route to handle status updates
@blueprint.route('/update_status', methods=['POST'])
@login_required
def update_status():
    try:
        video_id = request.form.get('video_id')
        status_type = request.form.get('status_type')

        success, updated_status = toggle_status(video_id, status_type)

        if success:
            return jsonify({'success': True, 'new_status': updated_status})
        else:
            return jsonify({'success': False, 'message': 'Failed to update status'})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error updating status: {str(e)}")
        db.session.rollback()  # Rollback changes in case of an error
        return jsonify({'success': False, 'message': 'An error occurred while updating status'})


def toggle_status(video_id, status_type):
    try:
        video = Video.query.get(video_id)
        if status_type == 'watched':
            video.watched = not video.watched
            updated_status = video.watched
        elif status_type == 'to_download':
            video.to_download = not video.to_download
            updated_status = video.to_download
        elif status_type == 'deleted':
            video.deleted = not video.deleted
            updated_status = video.deleted
        video.modified = func.now()
        db.session.commit()

        return True, updated_status  # Return success and updated status
    except Exception as e:
        # Log the exception for debugging
        print(f"Error toggling status: {str(e)}")
        db.session.rollback()  # Rollback changes in case of an error
        return False, None


@blueprint.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    video_id = request.form.get('video_id')
    playlist_id = request.form.get('playlist_id')

    try:
        # Retrieve the Video and Playlist objects from the database
        video = Video.query.get(video_id)
        playlist = Playlist.query.get(playlist_id)

        # Check if both video and playlist exist
        if video is not None and playlist is not None:
            # Add the video to the playlist
            video.playlist_id = playlist_id

            # Update last modified date
            video.modified = func.now()

            # Commit the changes to the database
            db.session.commit()

            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Video or playlist not found'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def str2bool(txt):
    if txt == '-1':
        return None
    else:
        return txt.lower() in ("yes", "true", "t", "1")

def boolstr2number(txt):
    rtrn = -1
    match txt:
        case "True":
            rtrn = 1
        case "False":
            rtrn = 0
        case _:
            rtrn = -1
    return rtrn

def sort2number(txt):
    rtrn = 0
    match txt:
        case "-1":
            rtrn = -1
        case "-2":
            rtrn = -2
        case "0":
            rtrn = 0
        case "1":
            rtrn = 1
        case _:
            rtrn = 0
    return rtrn

def encode_specific_characters(s, encoding='utf-16'):
    result = ''
    i = 0

    while i < len(s):
        char = s[i]

        # Check if the character is a high surrogate
        if 0xD800 <= ord(char) <= 0xDBFF:
            # Check if there is a following low surrogate
            if i + 1 < len(s):
                next_char = s[i + 1]
                if 0xDC00 <= ord(next_char) <= 0xDFFF:
                    # Encode the surrogate pair
                    encoded_chars = char + next_char
                    encoded_chars_bytes = encoded_chars.encode(encoding)
                    result += encoded_chars_bytes.decode('utf-16')  # Decode to replace the original characters
                    i += 2  # Skip the low surrogate
                    continue

        # Keep the character unchanged
        result += char
        i += 1

    print(result)
    return result