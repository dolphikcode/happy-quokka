# -*- encoding: utf-8 -*-

import json
import uuid
import random
from time import sleep
# from moviepy.editor import VideoFileClip

import requests
from sqlalchemy import func, desc, and_, select, alias

from apps.mytube import blueprint
from apps import db
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, current_app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from io import BytesIO
import os.path

from apps.mytube.forms import PlaylistForm, TagForm
from apps.home.models import *
from apps.mytube.models import *
from apps.authentication.models import UserConfig


@blueprint.route('/videos/<playlist_uuid>')
@login_required
def videos(playlist_uuid):
    time_start = datetime.now()
    # V
    v = request.args.get('v', '')
    if v != 'true':
        v = 'false'

    # Config
    current_time = datetime.now()
    read_config = db.session.scalars(
        db.select(UserConfig).filter_by(user_uuid=current_user.uuid, name='mytube')).first()

    if not read_config:
        read_config = UserConfig(
            user_uuid=current_user.uuid,
            name='mytube',
            config=json.dumps({
                'filter_watched': 'all',  # all, true, false
                'filter_to_download': 'all',  # all, true, false
                'filter_downloaded': 'all',  # all, true, false
                'sorted': 'created-desc',  # (asc or desc) released, created, visited, duration, channel(?)
                'limit': '100',
                'last_file_check': current_time.isoformat()
            }),
            modified=func.now(),
            uuid=str(uuid.uuid4())
        )
        db.session.add(read_config)
        db.session.commit()
    mytube_atributes = json.loads(read_config.config)

    # if file_check difference more than 15 min, send request to check files again
    check_file_exist_backend(datetime.fromisoformat(mytube_atributes['last_file_check']))

    # Sort videos
    column = 'created'
    order = mytube_atributes['sorted'].split("-")[1]
    match mytube_atributes['sorted'].split("-")[0]:
        case "released":
            column = 'release_date'
        case "created":
            column = 'created'
        case "visited":
            column = 'last_visited'
        case "duration":
            column = 'duration'
        case _:
            column = 'created'

    # Playlist
    playlist = Playlist()
    segment = ''
    pl_uuid = ''
    deleted = False
    title = ''
    if playlist_uuid == 'all':
        segment = 'mt_all'
        pl_uuid = None
        title = 'All videos'
        source = 'all'
        deleted = False
    elif playlist_uuid == 'trash':
        segment = 'mt_trash'
        pl_uuid = None
        deleted = True
        title = 'Deleted videos'
        source = 'trash'
    elif playlist_uuid == 'history':
        segment = 'mt_history'
        pl_uuid = None
        deleted = True
        title = 'History of watched videos'
        source = 'history'
    elif playlist_uuid == 'channel':
        segment = 'channel'
        pl_uuid = None
        deleted = False
        title = request.args.get('ch', '')
        source = 'channel'
        channel_name = request.args.get('ch', '')
    else:
        playlist = Playlist.query.filter_by(uuid=playlist_uuid).first()
        playlist.last_used = func.now()
        db.session.commit()
        deleted = False
        segment = playlist.name
        pl_uuid = playlist_uuid
        title = playlist.name
        source = playlist_uuid

    if playlist_uuid == 'channel':
        videos = (db.session.scalars(db.select(Video)
        .filter_by(user_uuid=current_user.uuid)
        .filter_by(deleted=False)
        .filter_by(channel=channel_name)
        .filter_by(v=str2bool(v))
        .order_by(
            getattr(Video, column).asc() if order == 'asc' else getattr(Video, column).desc()))
                  .all())
    elif playlist_uuid == 'history':
        videos = (db.session.query(Video)
                  .filter(Video.user_uuid == current_user.uuid,
                          Video.last_visited.isnot(None))
                  .filter(Video.v == str2bool(v))
                  .order_by(desc(Video.last_visited))
                  .all())
    elif playlist_uuid == 'all':
        videos = (
            db.session.query(Video)
            .filter(Video.user_uuid == current_user.uuid)
            .filter(Video.deleted == deleted)
            .filter(Video.v == str2bool(v))
            .order_by(
                getattr(Video, column).asc() if order == 'asc' else getattr(Video, column).desc())
            .all()
        )
    else:
        videos = (
            db.session.query(Video)
            .join(PlaylistVideo, PlaylistVideo.video_uuid == Video.uuid)
            # .join(Playlist, Playlist.uuid == PlaylistVideo.playlist_uuid)
            .filter(Video.user_uuid == current_user.uuid)
            .filter(PlaylistVideo.playlist_uuid == pl_uuid)
            # .filter(PlaylistVideo.status is True)
            .filter(Video.deleted == deleted)
            .filter(Video.v == str2bool(v))
            .order_by(
                getattr(Video, column).asc() if order == 'asc' else getattr(Video, column).desc())
            .all()
        )

    videos_to_load = []
    for v in videos:
        video_folder = current_app.config['VIDEO_ROOT']
        # Check arguments
        if source != 'random':
            if mytube_atributes['filter_watched'] != 'all':
                if v.watched != str2bool(mytube_atributes['filter_watched']):
                    continue
            if mytube_atributes['filter_to_download'] != 'all':
                if v.to_download != str2bool(mytube_atributes['filter_to_download']):
                    continue

        # Check if downloaded file exists in video folder
        # CHANGED TO CHECK IN DB
        if mytube_atributes['filter_downloaded'] != 'all' and source != 'random':
            if v.file_exist != str2bool(mytube_atributes['filter_downloaded']):
                continue
        videos_to_load.append(v.id)

    videos_count = len(videos_to_load)

    # Save to temporary table
    temporary_videos = db.session.scalars(
        db.select(LoadMore).filter_by(user_uuid=current_user.uuid)).first()

    if not temporary_videos:
        temporary_videos = LoadMore(
            user_uuid=current_user.uuid,
            data=json.dumps(videos_to_load),
        )
        db.session.add(temporary_videos)
    else:
        temporary_videos.data = json.dumps(videos_to_load)
    db.session.commit()

    time_end = datetime.now()
    time_delta = time_end - time_start
    print(f'Getting data from database: {time_delta}')

    return render_template('mytube/videos.html',
                           header=prepare_header(title, source),
                           videos_count=videos_count,
                           videos=prepare_videos(json.loads(read_config.config)['limit'], source),
                           segment=segment,
                           playlists=get_playlists(),
                           tags=db.session.scalars(db.select(Tag).filter_by(user_uuid=current_user.uuid)).all()
                           )
    # return render_template('mytube/videos.html',
    #                        title=playlist.name,
    #                        segment=playlist.name,
    #                        videos=videos,
    #                        count=len(videos),
    #                        playlists=get_playlists(),
    #                        convert_seconds_to_hms=convert_seconds_to_hms,
    #                        convert_int_date_to_iso=convert_int_date_to_iso,
    #                        get_playlist_name=get_playlist_name)


def prepare_header(title, source):
    read_config = db.session.scalars(
        db.select(UserConfig).filter_by(user_uuid=current_user.uuid, name='mytube')).first()

    sort_atributes = json.loads(read_config.config)
    # Create structure

    header = {
        'title': title,
        'fWatched': json.loads(read_config.config)['filter_watched'],
        'fToDownload': json.loads(read_config.config)['filter_to_download'],
        'fDownloaded': json.loads(read_config.config)['filter_downloaded'],
        'sorted': json.loads(read_config.config)['sorted'],
        'source': source,
        'limit': json.loads(read_config.config)['limit'],
    }

    return header


def prepare_videos(limit, source):
    time_start = datetime.now()
    read_config = db.session.scalars(
        db.select(UserConfig).filter_by(user_uuid=current_user.uuid, name='mytube')).first()

    sort_atributes = json.loads(read_config.config)
    # Create structure
    temporary_videos = db.session.scalars(
        db.select(LoadMore).filter_by(user_uuid=current_user.uuid)).first()
    videos_to_load = json.loads(temporary_videos.data)
    videos = []

    # Process each video
    video_folder = current_app.config['VIDEO_ROOT']

    while videos_to_load:
        v = db.session.query(Video).filter_by(id=videos_to_load[0]).first()
        # Check arguments
        if source != 'random':
            if sort_atributes['filter_watched'] != 'all':
                if v.watched != str2bool(sort_atributes['filter_watched']):
                    continue
            if sort_atributes['filter_to_download'] != 'all':
                if v.to_download != str2bool(sort_atributes['filter_to_download']):
                    continue

        if sort_atributes['filter_downloaded'] != 'all' and source != 'random':
            if v.file_exist != str2bool(sort_atributes['filter_downloaded']):
                continue

        # Check if audio file exists
        audio_found = False
        fname_audio = os.path.join(video_folder, f'{v.youtube_id}.mp3')
        if os.path.isfile(fname_audio):
            audio_found = True

        # Construct subquery to retrieve tag_uuids
        tagvideo_alias = alias(TagVideo)
        tag_subquery = (
            db.session.query(tagvideo_alias.c.tag_uuid)
            .filter(
                (tagvideo_alias.c.user_uuid == current_user.uuid) &
                (tagvideo_alias.c.video_uuid == v.uuid) &
                (tagvideo_alias.c.status == True)
            )
            .subquery()
        )

        # Query Tag names using the subquery
        existing_tag_names = (
            db.session.query(Tag.name)
            .join(tag_subquery, Tag.uuid == tag_subquery.c.tag_uuid)
            .all()
        )

        # Extract playlist names from list of tuples
        tag_names = [name for (name,) in existing_tag_names]

        # Construct subquery to retrieve playlist_uuids
        playlistvideo_alias = alias(PlaylistVideo)
        subquery = (
            select(playlistvideo_alias.c.playlist_uuid)
            .where(
                (playlistvideo_alias.c.user_uuid == current_user.uuid) &
                (playlistvideo_alias.c.video_uuid == v.uuid) &
                (playlistvideo_alias.c.status == True)
            )
            .alias("subquery")
        )

        # Query Playlist names using the subquery
        existing_playlists_names = (
            db.session.query(Playlist.name)
            .join(subquery, Playlist.uuid == subquery.c.playlist_uuid)
            .all()
        )

        # Extract playlist names from list of tuples
        playlist_names = [name for (name,) in existing_playlists_names]

        processed_video = {
            'id': v.id,
            'youtube_id': v.youtube_id,
            'user_uuid': v.user_uuid,
            'title': json.loads(v.title),
            'url': v.url,
            'description': json.loads(v.description),
            'channel': v.channel,
            'channel_url': v.channel_url,
            'thumbnail': url_for('static', filename=f'thumbs/{v.youtube_id}.jpg'),
            'duration': convert_seconds_to_hms(v.duration),
            'watched': v.watched,
            'deleted': v.deleted,
            'to_download': v.to_download,
            'video_exist': v.file_exist,
            'audio_exist': audio_found,
            'release_date': convert_int_date_to_iso(v.release_date),
            'created': v.created,
            'modified': v.modified,
            'comment': v.comment,
            'rate': v.rate,
            'uuid': v.uuid,
            # 'tags_selected': existing_tags_uuids,
            'tag_names': tag_names,
            'tags_count': len(tag_names),
            # 'playlists_selected': existing_playlists_uuids,
            'playlists_count': len(playlist_names),
            'playlist_names': playlist_names,
        }
        videos.append(processed_video)
        videos_to_load.pop(0)  # remove first item
        if len(videos) >= int(limit) or not videos_to_load:
            temporary_videos.data = json.dumps(videos_to_load)
            db.session.commit()
            break

    time_end = datetime.now()
    time_delta = time_end - time_start
    print(f'Preparing videos: {time_delta}')

    return videos


@blueprint.route('/load_more/<limit>/<source>')
@login_required
def load_more(limit, source):
    data = prepare_videos(limit, source)

    return render_template('mytube/load_more.html', videos=data)


@blueprint.route('/sort_filter/<source>/<obiekt>/<atrib>')
@login_required
def sort_filter(source, obiekt, atrib):
    read_config = db.session.scalars(
        db.select(UserConfig).filter_by(user_uuid=current_user.uuid, name='mytube')).first()
    sort_atributes = json.loads(read_config.config)

    # Define a mapping for attribute toggling
    toggle_mapping = {
        'all': 'true',
        'true': 'false',
        'false': 'all',
    }

    # Exchanging values for sort & filter
    match obiekt:
        case "watched":
            sort_atributes['filter_watched'] = toggle_mapping.get(atrib, atrib)
        case "to_download":
            sort_atributes['filter_to_download'] = toggle_mapping.get(atrib, atrib)
        case "downloaded":
            sort_atributes['filter_downloaded'] = toggle_mapping.get(atrib, atrib)
        case "sorted":
            sort_atributes['sorted'] = atrib
        case "limit":
            sort_atributes['limit'] = atrib
        case _:
            pass

    read_config.config = json.dumps(sort_atributes)
    db.session.commit()

    return redirect(url_for('mytube_blueprint.videos', playlist_uuid=source))


@blueprint.route('/')
@login_required
def mytube():
    # row_count = db.session.query(func.count()).select_from(Video).scalar()
    videos_to_load = []

    while len(videos_to_load) < 9:
        random_number = random.randint(1, 2000)  #row_count - 1)
        video = Video.query.get(random_number)

        if video.deleted is False and video.v is False:
            videos_to_load.append(video.id)

    # Save to temporary table
    temporary_videos = db.session.scalars(
        db.select(LoadMore).filter_by(user_uuid=current_user.uuid)).first()

    if not temporary_videos:
        temporary_videos = LoadMore(
            user_uuid=current_user.uuid,
            data=json.dumps(videos_to_load),
        )
        db.session.add(temporary_videos)
    else:
        temporary_videos.data = json.dumps(videos_to_load)
    db.session.commit()

    return render_template('mytube/mytube.html',
                           header=prepare_header("All Videos", 'random'),
                           videos=prepare_videos('9', 'random'),
                           segment='mytube',
                           playlists=get_playlists(),
                           tags=db.session.scalars(db.select(Tag).filter_by(user_uuid=current_user.uuid)).all()
                           )


@blueprint.route('/video/<video_uuid>')
@login_required
def video(video_uuid):
    video = db.session.scalars(db.select(Video).filter_by(uuid=video_uuid)).first()
    video.last_visited = func.now()
    video.modified = func.now()
    db.session.commit()
    tags = db.session.scalars(
        db.select(Tag).filter_by(user_uuid=current_user.uuid).order_by(getattr(Tag, 'group').asc())).all()
    video_folder = current_app.config['VIDEO_ROOT']

    # Check if downloaded file exists in video folder
    file_found = False
    video_path = ''
    fname1 = os.path.join(video_folder, f'{video.youtube_id}.mp4')
    fname2 = os.path.join(video_folder, f'{video.youtube_id}.webm')
    if os.path.isfile(fname1):
        file_found = True
        video_path = url_for('static', filename=f'videos/{video.youtube_id}.mp4')
    elif os.path.isfile(fname2):
        file_found = True
        video_path = url_for('static', filename=f'videos/{video.youtube_id}.webm')

    # Check if audio file exists
    audio_found = False
    audio_path = ''
    fname_audio = os.path.join(video_folder, f'{video.youtube_id}.mp3')
    if os.path.isfile(fname_audio):
        audio_found = True
        audio_path = url_for('static', filename=f'videos/{video.youtube_id}.mp3')

    # # Query existing TagVideo objects for the current user and video_uuid
    # existing_tags = TagVideo.query.filter_by(
    #     user_uuid=current_user.uuid,
    #     video_uuid=video_uuid,
    #     status=True
    # ).all()
    #
    # # Extract tag_uuids from existing TagVideo objects
    # existing_tags_uuids = [tag.tag_uuid for tag in existing_tags]
    #
    # existing_tags_names = []
    # for et in existing_tags_uuids:
    #     existing_tags_names.append(db.session.scalars(db.select(Tag).filter_by(uuid=et)).first().name)

    # # Construct subquery to retrieve tag_uuids
    # tag_subquery = select([TagVideo.tag_uuid]).where(
    #     TagVideo.user_uuid == current_user.uuid,
    #     TagVideo.video_uuid == video.uuid,
    #     TagVideo.status == True,
    # ).alias("tag_subquery")
    #
    # # Query Tag names using the subquery
    # existing_tag_names = (
    #     db.session.query(Tag.name)
    #     .join(tag_subquery, Tag.uuid == tag_subquery.c.tag_uuid)
    #     .all()
    # )
    #
    # # Extract playlist names from list of tuples
    # tag_names = [name for (name,) in existing_tag_names]
    #
    # # Construct subquery to retrieve playlist_uuids
    # subquery = select([PlaylistVideo.playlist_uuid]).where(
    #     PlaylistVideo.user_uuid == current_user.uuid,
    #     PlaylistVideo.video_uuid == video.uuid,
    #     PlaylistVideo.status == True,
    # ).alias("subquery")
    #
    # # Query Playlist names using the subquery
    # existing_playlists_names = (
    #     db.session.query(Playlist.name)
    #     .join(subquery, Playlist.uuid == subquery.c.playlist_uuid)
    #     .all()
    # )
    # Construct subquery to retrieve tag_uuids
    tagvideo_alias = alias(TagVideo)
    tag_subquery = (
        db.session.query(tagvideo_alias.c.tag_uuid)
        .filter(
            (tagvideo_alias.c.user_uuid == current_user.uuid) &
            (tagvideo_alias.c.video_uuid == video.uuid) &
            (tagvideo_alias.c.status == True)
        )
        .subquery()
    )

    # Query Tag names using the subquery
    existing_tag_names = (
        db.session.query(Tag.name)
        .join(tag_subquery, Tag.uuid == tag_subquery.c.tag_uuid)
        .all()
    )

    # Extract playlist names from list of tuples
    tag_names = [name for (name,) in existing_tag_names]

    # Construct subquery to retrieve playlist_uuids
    playlistvideo_alias = alias(PlaylistVideo)
    subquery = (
        select(playlistvideo_alias.c.playlist_uuid)
        .where(
            (playlistvideo_alias.c.user_uuid == current_user.uuid) &
            (playlistvideo_alias.c.video_uuid == video.uuid) &
            (playlistvideo_alias.c.status == True)
        )
        .alias("subquery")
    )

    # Query Playlist names using the subquery
    existing_playlists_names = (
        db.session.query(Playlist.name)
        .join(subquery, Playlist.uuid == subquery.c.playlist_uuid)
        .all()
    )

    # Extract playlist names from list of tuples
    playlist_names = [name for (name,) in existing_playlists_names]

    chapters = []
    for chapter in json.loads(video.chapters):
        processed_chapter = {
            's': int(chapter['s']),
            'e': int(chapter['e']),
            'n': chapter['n'],
        }
        chapters.append(processed_chapter)

    processed_video = {
        'id': video.id,
        'uuid': video.uuid,
        'youtube_id': video.youtube_id,
        'user_uuid': video.user_uuid,
        'title': json.loads(video.title),
        'url': video.url,
        'description': json.loads(video.description),
        'channel': video.channel,
        'channel_url': video.channel_url,
        'duration': convert_seconds_to_hms(video.duration),
        'watched': video.watched,
        'deleted': video.deleted,
        'to_download': video.to_download,
        'video_exist': file_found,
        'video_path': video_path,
        'audio_exist': audio_found,
        'audio_path': audio_path,
        'release_date': convert_int_date_to_iso(video.release_date),
        'created': video.created,
        'modified': video.modified,
        'comment': video.comment,
        'rate': video.rate,
        # 'playlist_id': playlist.id,
        # 'playlist_name': playlist.name,
        # 'tags_selected': existing_tags_uuids,
        # 'tags_selected_names': existing_tags_names,
        'tag_names': tag_names,
        'tags_count': len(tag_names),
        # 'playlists_selected': existing_playlists_uuids,
        'playlists_count': len(playlist_names),
        'playlist_names': playlist_names,
        'chapters': chapters,
    }

    return render_template('mytube/video.html',
                           video=processed_video,
                           # chapters=chapters,
                           tags=tags,
                           playlists=get_playlists(),
                           convert_seconds_to_hms=convert_seconds_to_hms,
                           segment='mytube')


@blueprint.route('/playlist/create', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()

    if form.validate_on_submit():
        new_playlist = Playlist(
            user_uuid=current_user.uuid,
            name=form.name.data,
            last_used=func.now(),
            modified=func.now(),
            uuid=str(uuid.uuid4())
        )
        db.session.add(new_playlist)

        db.session.commit()
        return redirect(url_for('mytube_blueprint.mytube'))

    return render_template('mytube/create_playlist.html', form=form)


@blueprint.route('/playlist/<int:playlist_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_playlist(playlist_id):
    form = PlaylistForm()
    playlist = Playlist.query.get(playlist_id)
    if request.method == 'POST':
        playlist.name = request.form['name']

        db.session.commit()
        return redirect(url_for('mytube_blueprint.mytube'))
    return render_template('mytube/create_playlist.html', playlist=playlist, form=form)


def get_playlists():
    playlists = db.session.scalars(db.select(Playlist).order_by(desc(Playlist.last_used))).all()
    return playlists


def get_playlist(movie_uuid):
    if movie_uuid:
        playlist = Playlist.query.filter_by(uuid=movie_uuid).first()
    else:
        playlist = Playlist()
        playlist.id = 0
    return playlist


def get_playlist_name(playlist_id):
    if playlist_id:
        playlist = Playlist.query.get(playlist_id)
        return playlist.name
    else:
        return ''


@blueprint.route('/tag/create', methods=['GET', 'POST'])
@login_required
def create_tag():
    form = TagForm()

    if form.validate_on_submit():
        new_tag = Tag(
            user_uuid=current_user.uuid,
            name=form.name.data,
            group=form.group.data,
            modified=func.now(),
            uuid=str(uuid.uuid4())
        )
        db.session.add(new_tag)

        db.session.commit()
        return redirect(url_for('mytube_blueprint.mytube'))

    return render_template('mytube/create_tag.html', form=form)


@blueprint.route('/tag/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    form = TagForm()
    tag = Tag.query.get(tag_id)
    if request.method == 'POST':
        tag.name = request.form['name']
        tag.group = request.form['group']

        db.session.commit()
        return redirect(url_for('mytube_blueprint.mytube'))
    return render_template('mytube/create_tag.html', tag=tag, form=form)


# Route to display video thumbnail
@blueprint.route('/video_thumbnail/<int:video_id>')
@login_required
def display_thumbnail(video_id):
    vid = Video.query.get(video_id)

    if vid and vid.thumbnail:
        return send_file(BytesIO(vid.thumbnail), mimetype='image/jpeg')
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
        if hours > 99:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
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


# Route to handle stars updates
@blueprint.route('/update_stars', methods=['POST'])
@login_required
def update_stars():
    try:
        video_id = request.form.get('video_id')
        stars = request.form.get('stars')

        success, updated_stars = toggle_stars(video_id, stars)

        if success:
            return jsonify({'success': True, 'new_status': updated_stars})
        else:
            return jsonify({'success': False, 'message': 'Failed to update stars'})
    except Exception as e:
        # Log the exception for debugging
        print(f"Error updating status: {str(e)}")
        db.session.rollback()  # Rollback changes in case of an error
        return jsonify({'success': False, 'message': 'An error occurred while updating stars'})


def toggle_stars(video_id, stars):
    try:
        video = Video.query.get(video_id)
        video.rate = int(stars)
        updated_stars = video.rate
        video.modified = func.now()
        video.last_visited = func.now()

        db.session.commit()

        return True, updated_stars  # Return success and updated status
    except Exception as e:
        # Log the exception for debugging
        print(f"Error toggling status: {str(e)}")
        db.session.rollback()  # Rollback changes in case of an error
        return False, None


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
            video.playlist_uuid = playlist.uuid

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


@blueprint.route('/update_playback_time', methods=['POST'])
def update_playback_time():
    video_id = request.form.get('video_id')
    current_time = request.form.get('current_time')

    video = db.session.get(Video, video_id)
    video.video_position = current_time
    video.modified = func.now()
    video.last_visited = func.now()

    db.session.commit()

    return jsonify({'success': True})


@blueprint.route('/get_playback_time/<int:video_id>')
def get_playback_time(video_id):
    try:
        # Fetch the video object and its playback time
        video = db.session.get(Video, video_id)
        playback_time = video.video_position

        # Return the playback time as JSON
        return jsonify({'success': True, 'playback_time': playback_time})
    except Exception as e:
        # Handle the exception and return an error response
        return jsonify({'success': False, 'error': str(e)})


@blueprint.route('/download_creator_playlist', methods=['GET', 'POST'])
def download_creator_playlist():
    if request.method == 'POST':
        playlist_id = ''
        playlist_id = request.form.get('playlist_id')
        if playlist_id == '' or playlist_id == None:
            playlist_id = '0'
        add_to_database = request.form.get('add_to_database')

        # Check if the "Add to database" checkbox is checked
        if add_to_database:
            to_database = 1
        else:
            to_database = 0
        # Call the API with playlist_id and add_to_database
        api_link = current_app.config['API_LINK']
        api_url = f'{api_link}/get_info/{current_user.id}/{playlist_id}/{str(to_database)}'
        print(api_url)

        # Example using the requests library
        response = requests.get(api_url)
        if response.status_code == 200:
            print(response)
        else:
            print(response)

        return redirect(url_for('mytube_blueprint.mytube'))  # Redirect after processing

    playlists = CreatorPlaylist.query.all()
    return render_template('mytube/download_creator_playlist.html', playlists=playlists)


@blueprint.route('/download_movies', methods=['GET'])
def download_movies():
    api = (db.session.scalars(db.select(ApiExchange)
                              .filter_by(user_uuid=current_user.uuid, module='download_movies'))
           .first())
    try:
        api_command = json.loads(api.command)
    except:
        pass
    if not api:
        api = ApiExchange()
        api.user_uuid = current_user.uuid
        api.uuid = str(uuid.uuid4())
        api.status = 'starting download'
        api.modified = datetime.utcnow()
        api.module = 'download_movies'
        api.command = json.dumps({
            'run': True
        })
        db.session.add(api)
    elif not api_command['run']:
        api.command = json.dumps({
            'run': True
        })
    # else:
    #     return redirect(url_for('mytube_blueprint.mytube'))  # Redirect after processing
    db.session.commit()

    # Call the API with playlist_id and add_to_database
    api_link = current_app.config['API_LINK']
    api_url = f'{api_link}/download_movies/{current_user.id}'

    # Example using the requests library
    response = requests.get(api_url)
    if response.status_code == 200:
        print(response)
    else:
        print(response)

    return redirect(url_for('mytube_blueprint.mytube'))  # Redirect after processing


@blueprint.route('/download_cancel', methods=['GET'])
def download_cancel():
    api = (db.session.scalars(db.select(ApiExchange)
                              .filter_by(user_uuid=current_user.uuid, module='download_movies'))
           .first())
    api.command = json.dumps({
        'run': False
    })
    db.session.commit()

    return redirect(url_for('mytube_blueprint.mytube'))  # Redirect after processing


@blueprint.route('/download_movie/<video_uuid>/<quality>', methods=['GET'])
def download_movie(video_uuid, quality):
    # Call the API with playlist_id and add_to_database
    api_link = current_app.config['API_LINK']
    api_url = f'{api_link}/download_movie/{video_uuid}/{quality}'

    # Example using the requests library
    response = requests.get(api_url)
    if response.status_code == 200:
        print(response)
    else:
        print(response)

    return redirect(url_for('mytube_blueprint.video', video_uuid=video_uuid))  # Redirect after processing


@blueprint.route('/get_audio/<video_uuid>', methods=['GET'])
@login_required
def get_audio(video_uuid):
    # Call the API with playlist_id and add_to_database
    api_link = current_app.config['API_LINK']
    api_url = f'{api_link}/get_audio/{video_uuid}'
    print(api_url)

    # Example using the requests library
    response = requests.get(api_url)
    if response.status_code == 200:
        print(response)
    else:
        print(response)

    return redirect(url_for('mytube_blueprint.video', video_uuid=video_uuid))  # Redirect after processing


@blueprint.route('/download_thumbnail/<video_uuid>', methods=['GET'])
@login_required
def download_thumbnail(video_uuid):
    # Call the API with playlist_id and add_to_database
    api_link = current_app.config['API_LINK']
    api_url = f'{api_link}/get_thumbnail/{video_uuid}'
    print(api_url)

    # Example using the requests library
    response = requests.get(api_url)
    if response.status_code == 200:
        print(response)
    else:
        print(response)

    return redirect(url_for('mytube_blueprint.video', video_uuid=video_uuid))  # Redirect after processing


@blueprint.route('/clean_deleted', methods=['GET'])
@login_required
def clean_deleted():
    # Call the API with playlist_id and add_to_database
    api_link = current_app.config['API_LINK']
    api_url = f'{api_link}/clean_deleted/{current_user.id}'

    # Example using the requests library
    response = requests.get(api_url)
    if response.status_code == 200:
        print(response)
    else:
        print(response)

    return redirect(url_for('mytube_blueprint.mytube'))  # Redirect after processing


@blueprint.route('/clean_deleted', methods=['GET'])
@login_required
def check_file_exist_backend(last_check_date):
    # last_file_check = datetime.fromisoformat(last_check_date)
    # last_file_check = datetime.strptime(last_check_date, "%Y-%m-%d %H:%M:%S.%f")
    time_difference = datetime.now() - last_check_date
    time_difference_seconds = int(time_difference.total_seconds())
    if time_difference_seconds > 900:
        try:
            # Call the API with playlist_id and add_to_database
            api_link = current_app.config['API_LINK']
            api_url = f'{api_link}/update_file_exist/{current_user.id}'

            # Example using the requests library
            response = requests.get(api_url)
            if response.status_code == 200:
                print(response)
            else:
                print(response)
        except requests.exceptions.RequestException as e:
            print(f"No connection to BACKEND: {e}")

    return True


@blueprint.route('/prepare_list')
@login_required
def prepare_list():
    videos = []
    vids = (db.session.scalars(db.select(Video)
                               .filter_by(user_uuid=current_user.uuid)
                               .filter_by(deleted=False)
                               .filter_by(to_download=True)
                               .order_by(getattr(Video, 'created').desc()))
            .all())

    video_folder = current_app.config['VIDEO_ROOT']
    for v in vids:
        # Check if downloaded file exists
        fname = os.path.join(video_folder, f'{v.youtube_id}.mp4')
        if not os.path.isfile(fname):
            processed_video = {
                'youtube_id': v.youtube_id,
                'url': v.url,
            }
            videos.append(processed_video)

    return json.dumps(videos)


@blueprint.route('/tag_video', methods=['POST'])
@login_required
def tag_video():
    try:
        data = request.get_json()
        tags_selected = data.get('tags', [])
        video_uuid = data.get('video_uuid', '')

        # Query existing TagVideo objects for the current user and video_uuid
        existing_tags = TagVideo.query.filter_by(
            user_uuid=current_user.uuid,
            video_uuid=video_uuid
        ).all()

        # Extract tag_uuids from existing TagVideo objects
        existing_tags_uuids = [tag.tag_uuid for tag in existing_tags]

        # Identify tags to be added, updated, and deleted
        tags_to_add = set(tags_selected) - set(existing_tags_uuids)
        tags_to_delete = set(existing_tags_uuids) - set(tags_selected)

        # Create new TagVideo entries for tags to be added
        for tag_uuid in tags_to_add:
            new_tag_video = TagVideo(
                tag_uuid=tag_uuid,
                video_uuid=video_uuid,
                user_uuid=current_user.uuid,
                uuid=str(uuid.uuid4()),
                status=True
            )
            db.session.add(new_tag_video)

        # Update status for existing TagVideo entries with selected tags
        for tag_video in existing_tags:
            if tag_video.tag_uuid in tags_selected:
                tag_video.status = True
            else:
                # Update status for TagVideo entries to be deleted
                tag_video.status = False
            tag_video.modified = func.now()

        # Commit changes to the database
        db.session.commit()

        # For example, print the received data
        print(f"Received data - Video UUID: {video_uuid}, Tags: {tags_selected}")

        # You can send a response back to the client
        response_data = {'message': 'Tags processed successfully'}
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@blueprint.route('/get_selected_tags', methods=['POST'])
@login_required
def get_selected_tags():
    try:
        data = request.get_json()
        video_uuid = data.get('video_uuid', '')

        # Query existing TagVideo objects for the current user and video_uuid
        existing_tags = TagVideo.query.filter_by(
            user_uuid=current_user.uuid,
            video_uuid=video_uuid,
            status=True,
        ).all()

        # Extract tag_uuids from existing TagVideo objects
        existing_tags_uuids = [tag.tag_uuid for tag in existing_tags]

        # Send a response back to the client
        response_data = {'tags': existing_tags_uuids}
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@blueprint.route('/playlist_video', methods=['POST'])
@login_required
def playlist_video():
    try:
        data = request.get_json()
        playlists_selected = data.get('playlists', [])
        video_uuid = data.get('video_uuid', '')

        # Query existing PlaylistVideo objects for the current user and video_uuid
        existing_playlists = PlaylistVideo.query.filter_by(
            user_uuid=current_user.uuid,
            video_uuid=video_uuid
        ).all()

        # Extract tag_uuids from existing TagVideo objects
        existing_playlists_uuids = [playlist.playlist_uuid for playlist in existing_playlists]

        # Identify playlists to be added, updated, and deleted
        playlists_to_add = set(playlists_selected) - set(existing_playlists_uuids)
        playlists_to_delete = set(existing_playlists_uuids) - set(playlists_selected)

        # Create new TagVideo entries for tags to be added
        for playlist_uuid in playlists_to_add:
            new_playlist_video = PlaylistVideo(
                playlist_uuid=playlist_uuid,
                video_uuid=video_uuid,
                user_uuid=current_user.uuid,
                uuid=str(uuid.uuid4()),
                status=True
            )
            db.session.add(new_playlist_video)

        # Update status for existing PlaylistVideo entries with selected tags
        for playlist_video in existing_playlists:
            if playlist_video.playlist_uuid in playlists_selected:
                playlist_video.status = True
            else:
                # Update status for PlaylistVideo entries to be deleted
                playlist_video.status = False
            playlist_video.modified = func.now()

        # Commit changes to the database
        db.session.commit()

        # For example, print the received data
        print(f"Received data - Video UUID: {video_uuid}, Tags: {playlists_selected}")

        # You can send a response back to the client
        response_data = {'message': 'Playlists processed successfully'}
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@blueprint.route('/get_selected_playlists', methods=['POST'])
@login_required
def get_selected_playlists():
    try:
        data = request.get_json()
        video_uuid = data.get('video_uuid', '')
        print(video_uuid)

        # Query existing PlaylistVideo objects for the current user and video_uuid
        existing_playlists = PlaylistVideo.query.filter_by(
            user_uuid=current_user.uuid,
            video_uuid=video_uuid,
            status=True,
        ).all()

        # Extract playlist_uuids from existing PlaylistVideo objects
        existing_playlists_uuids = [playlist.playlist_uuid for playlist in existing_playlists]

        # Send a response back to the client
        response_data = {'playlists': existing_playlists_uuids}
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@blueprint.route('/videos_add', methods=['POST'])
@login_required
def videos_add():
    try:
        data = request.get_json()
        videos_to_add = data.get('videos', [])

        for v in videos_to_add:
            add_video = VideoToProcess(
                youtube_id=v,
                user_uuid=current_user.uuid,
                uuid=str(uuid.uuid4()),
                status=0
            )
            db.session.add(add_video)

        # Commit changes to the database
        db.session.commit()

        # Call the API with playlist_id and add_to_database
        api_link = current_app.config['API_LINK']
        api_url = f'{api_link}/new_get_info/{current_user.id}'

        # Example using the requests library
        response = requests.get(api_url)
        if response.status_code == 200:
            print(response)
        else:
            print(response)

        # You can send a response back to the client
        response_data = {'message': 'Videos added successfully'}
        return jsonify(response_data), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred'}), 500


@blueprint.route('/make_v/<video_uuid>', methods=['GET'])
@login_required
def make_v(video_uuid):
    v = Video.query.filter_by(uuid=video_uuid).first()
    v.v = True
    v.modified = func.now()

    db.session.commit()
    return redirect(url_for('mytube_blueprint.video', video_uuid=video_uuid))  # Redirect after processing
