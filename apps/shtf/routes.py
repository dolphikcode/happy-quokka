# -*- encoding: utf-8 -*-

import json
import uuid
import random

import pytz
import requests
from sqlalchemy import func, desc, and_, select, cast, Text

from apps.shtf import blueprint
from apps import db
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, current_app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from io import BytesIO
import os.path

# from apps.home.models import *
from apps.shtf.models import *
from apps.authentication.models import UserConfig
from apps.shtf.forms import ActivityForm

from ticktick.oauth2 import OAuth2  # OAuth2 Manager
from ticktick.api import TickTickClient  # Main Interface
from ticktick.helpers.time_methods import convert_date_to_tick_tick_format as tick_time_convert


@blueprint.route('/')
@login_required
def do_stuff():
    test = tick_config()
    # Config
    read_config = db.session.scalars(
        db.select(UserConfig).filter_by(user_uuid=current_user.uuid, name='shtf')).first()

    if not read_config:
        read_config = UserConfig(
            user_uuid=current_user.uuid,
            name='shtf',
            config=json.dumps({
                'filter_completed': 'all',  # all, true, false
                # 'filter_to_download': 'all',  # all, true, false
                # 'filter_downloaded': 'all',  # all, true, false
                'sorted': 'due-date',  # (asc or desc) released, created, visited, duration, channel(?)
                'limit': '100'
            }),
            modified=func.now(),
            uuid=str(uuid.uuid4())
        )
        db.session.add(read_config)
        db.session.commit()
    sort_atributes = json.loads(read_config.config)

    # Sort videos
    column = 'created'
    order = sort_atributes['sorted'].split("-")[1]
    match sort_atributes['sorted'].split("-")[0]:
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

    # =========== OTHER PART
    # Initialize variables
    conditions = []
    tags_to_search = []
    contexts_to_search = []
    boolean_condition = True
    integer_condition = 10
    due_date_condition = datetime(year=2024, month=3, day=10)

    # Project condition
    # conditions.append(cast(Task.project, Text).like('aaa'))

    # Loop through each tag and construct a condition
    for tag in tags_to_search:
        conditions.append(cast(Task.tags, Text).like(f'%"{tag}"%'))

    # Loop through each context and construct a condition
    for context in contexts_to_search:
        conditions.append(cast(Task.contexts, Text).like(f'%"{context}"%'))

    # Combine all conditions using the and_() operator
    query = and_(*conditions)

    # Search for videos with all tags in the list
    tasks = (Task.query
             .filter_by(user_uuid=current_user.uuid)
             .filter(query).all())

    print(tasks)

    return redirect(url_for('shtf_blueprint.shtf'))


@blueprint.route('/shtf')
@login_required
def shtf():
    return render_template('shtf/shtf.html',
                           segment='dostuff')


@blueprint.route('/activity/create', methods=['GET', 'POST'])
@login_required
def create_activity():
    form = ActivityForm()

    if form.validate_on_submit():
        new_activity = Activity(
            user_uuid=current_user.uuid,
            uuid=str(uuid.uuid4()),
            modified=func.now(),
            name=form.name.data,
            basic_pts_ratio=float(form.basic_points_ratio.data),
            added_pts_ratio=1.0,
            basic_health_ratio=float(form.basic_health_ratio.data),
            added_health_ratio=1.0,
        )
        db.session.add(new_activity)

        db.session.commit()
        return redirect(url_for('shtf_blueprint.shtf'))

    return render_template('shtf/create_activity.html', form=form)


@blueprint.route('/add')
@login_required
def task_add():
    new_task = Task(
        user_uuid=current_user.uuid,
        created=func.now(),
        modified=func.now(),
        name=f"{datetime.now()}",
        description=f"{datetime.now()}",
        difficulty=2,
        uuid=str(uuid.uuid4()),
        tags=json.dumps(['729ec604-a745-4c95-8ea1-6422fa606910', 'f317fc6e-b095-423e-ba9d-0a0591b966fe'])

    )
    db.session.add(new_task)

    db.session.commit()
    return redirect(url_for('mytube_blueprint.mytube'))


@blueprint.route('/tick_sync')
@login_required
def tick_sync():
    client = tick_authorize()

    # PROJECTS
    all_projects = client.state['projects']
    for p in all_projects:
        proj = db.session.scalars(
            select(Project).filter_by(user_uuid=current_user.uuid, tick_project_id=p['id'])).first()

        if not proj:
            new_project_from_tick(p)

    # UNCOMPLETED TASKS
    uncompleted_tasks = client.state['tasks']
    for t in uncompleted_tasks:
        task = db.session.scalars(
            select(Task).filter_by(user_uuid=current_user.uuid, tick_id=t['id'])).first()

        if not task:
            new_task_from_tick(t)
            print(f'{t}\n\n')
        else:
            modify_task(client, task, t)

    # COMPLETED TASKS
    date_now = datetime.now()  # (year=2024, month=3, day=25)
    date_begin = datetime(year=2024, month=1, day=1)
    completed_tasks = client.task.get_completed(date_begin, date_now)

    for t in completed_tasks:
        task = db.session.scalars(
            select(Task).filter_by(user_uuid=current_user.uuid, tick_id=t['id'])).first()

        if not task:
            new_task_from_tick(t)
            print(f'{t}\n\n')
        else:
            modify_task(client, task, t)

    # x = client.state.items()
    # # json_str = json.dumps(x)
    #
    # for c in completed:
    #     print(c)


# =======================  TASKS COMBINED WITH TICKTICK =================================
def new_task_from_tick(task_dict):
    task = Task(
        user_uuid=current_user.uuid,
        tick_id=task_dict['id'],
        name=task_dict['title'],
        description=check_key(task_dict, 'content'),
        status=task_dict['status'],
        created=tickdate_to_datetime(check_key(task_dict, 'modifiedTime'),
                                     check_key(task_dict, 'timeZone')),
        modified=tickdate_to_datetime(check_key(task_dict, 'modifiedTime'),
                                      check_key(task_dict, 'timeZone')),
        start_date=tickdate_to_datetime(check_key(task_dict, 'startDate'),
                                        check_key(task_dict, 'timeZone')),
        due_date=tickdate_to_datetime(check_key(task_dict, 'dueDate'),
                                      check_key(task_dict, 'timeZone')),
        project=task_dict['projectId'],  # or search for project_uuid
        tick_project_id=task_dict['projectId'],
        difficulty=task_dict['priority'],
        uuid=str(uuid.uuid4()),
        tags=json.dumps(check_key(task_dict, 'tags')),  # for now
        contexts=''
    )
    db.session.add(task)
    db.session.commit()


def modify_task(client, task, task_dict):
    """
    Check and modify task when synchronized with TickTick
    """
    tick_modified = tickdate_to_datetime(check_key(task_dict, 'modifiedTime'),
                                         check_key(task_dict, 'timeZone'))
    # NOTHING CHANGED
    if tick_modified == task.modified:
        return

    # TICKTICK TASK WAS CHANGED
    if tick_modified > task.modified:
        task.name = task_dict['title']
        task.description = check_key(task_dict, 'content')
        task.status = task_dict['status']
        task.modified = tickdate_to_datetime(check_key(task_dict, 'modifiedTime'),
                                             check_key(task_dict, 'timeZone'))
        task.start_date = tickdate_to_datetime(check_key(task_dict, 'startDate'),
                                               check_key(task_dict, 'timeZone'))
        task.due_date = tickdate_to_datetime(check_key(task_dict, 'dueDate'),
                                             check_key(task_dict, 'timeZone'))
        task.project = task_dict['projectId']  # or search for project_uuid
        task.tick_project_id = task_dict['projectId']
        task.difficulty = task_dict['priority']
        task.tags = json.dumps(check_key(task_dict, 'tags'))  # for now

        db.session.commit()
        return

    # LOCAL TASK WAS CHANGED
    if tick_modified < task.modified:
        tick_task = client.get_by_id(task_dict['id'])
        tick_task['title'] = task.name
        tick_task['content'] = task.description
        tick_task['status'] = task.status
        tick_task['modifiedTime'] = tick_time_convert(task.modified, tick_task['timeZone'])
        if task.start_date:
            tick_task['startDate'] = tick_time_convert(task.start_date, tick_task['timeZone'])
        if task.due_date:
            tick_task['dueDate'] = tick_time_convert(task.due_date, tick_task['timeZone'])
        tick_task['projectId'] = task.tick_project_id
        tick_task['priority'] = task.difficulty
        # tick_task['tags'] = task.tags     # for now not working
        client.task.update(tick_task)
        return


@blueprint.route('/tick_clean_completed')
@login_required
def tick_clean_completed():
    client = tick_authorize()
    date_now = datetime.now()  # (year=2024, month=3, day=25)
    date_begin = datetime(year=2024, month=1, day=1)
    completed_tasks = client.task.get_completed(date_begin, date_now)

    # tasks_to_delete = []
    # for t in completed_tasks:
    #     tasks_to_delete.append(t)
    deleted = client.task.delete(completed_tasks)
    return redirect(url_for('dostuff_blueprint.do_stuff'))


# =======================  PROJECTS COMBINED WITH TICKTICK =================================
def new_project_from_tick(proj_dict):
    proj = Project(
        user_uuid=current_user.uuid,
        tick_project_id=proj_dict['id'],
        name=proj_dict['name'],
        description='',
        status=0 if proj_dict['closed'] is None else 1,
        subproject_of='',  # to do later - TickTick folders
        created=tickdate_to_datetime(check_key(proj_dict, 'modifiedTime'),
                                     check_key(proj_dict, 'timeZone')),
        modified=tickdate_to_datetime(check_key(proj_dict, 'modifiedTime'),
                                      check_key(proj_dict, 'timeZone')),
        uuid=str(uuid.uuid4()),
        color=proj_dict['color'][1:],
        icon=''
    )
    db.session.add(proj)
    db.session.commit()


# =======================  TICKTICK AUTHENTICATION =================================
@login_required
def tick_authorize():
    session_attr = tick_config()

    auth_client = OAuth2(client_id=session_attr['client_id'],
                         client_secret=session_attr['client_secret'],
                         redirect_uri=session_attr['tick_uri'],
                         web_access=True,
                         cached_token_info=None if session_attr['tick_token'] == '' else json.loads(
                             session_attr['tick_token']))
    if session_attr['tick_token'] == '':
        url = auth_client.step1_url
        return redirect(auth_client.step1_url)

    client = TickTickClient(session_attr['tick_username'], session_attr['tick_password'], auth_client)
    return client


@blueprint.route('/tick_login')
@login_required
def tick_login():
    session_attr = tick_config()

    auth_client = OAuth2(client_id=session_attr['client_id'],
                         client_secret=session_attr['client_secret'],
                         redirect_uri=session_attr['tick_uri'],
                         web_access=True,
                         cached_token_info=None if session_attr['tick_token'] == '' else json.loads(
                             session_attr['tick_token']))
    if session_attr['tick_token'] == '':
        url = auth_client.step1_url
        return redirect(auth_client.step1_url)
    else:
        return redirect(url_for('dostuff_blueprint.do_stuff'))


@blueprint.route('/tick_login2')
@login_required
def tick_login2():
    session_attr = tick_config()
    code = request.args['code']
    state = request.args['state']
    # cached_token = {"access_token": "30af49eb-ecd1-4173-8984-a68da80caf88", "token_type": "bearer", "expires_in": 15186934, "scope": "tasks:read tasks:write", "expire_time": 1726571990, "readable_expire_time": "Tue Sep 17 13:19:50 2024"}

    auth_client = OAuth2(client_id=session_attr['client_id'],
                         client_secret=session_attr['client_secret'],
                         redirect_uri=session_attr['tick_uri'],
                         web_access=True,
                         cached_token_info=None if session_attr['tick_token'] == '' else session_attr['tick_token'])

    if session_attr['tick_token'] == '':
        token = auth_client.set_web_token(code)
        tick_save_token(token)

    return redirect(url_for('do_stuff'))


@login_required
def tick_config():
    # Config
    read_config = db.session.scalars(
        db.select(UserConfig).filter_by(user_uuid=current_user.uuid, name='tick_config')).first()

    if not read_config:
        read_config = UserConfig(
            user_uuid=current_user.uuid,
            name='tick_config',
            config=json.dumps({
                'client_id': '',
                'client_secret': '',
                'tick_username': '',
                'tick_password': '',
                'tick_uri': '',
                'tick_token': ''
            }),
            modified=func.now(),
            uuid=str(uuid.uuid4())
        )
        db.session.add(read_config)
        db.session.commit()
    session_atributes = json.loads(read_config.config)

    return session_atributes


@login_required
def tick_save_token(token):
    # Config
    read_config = db.session.scalars(
        db.select(UserConfig).filter_by(user_uuid=current_user.uuid, name='tick_config')).first()

    # Deserialize the JSON string stored in read_config.config into a dictionary
    config_dict = json.loads(read_config.config)

    # Modify the 'tick_token' key in the dictionary
    config_dict['tick_token'] = json.dumps(token)

    # Serialize the modified dictionary back to a JSON string
    read_config.config = json.dumps(config_dict)

    read_config.modified = func.now()
    db.session.commit()
    session_atributes = json.loads(read_config.config)

    return session_atributes


# =======================  OTHER METHODS  =================================
def tickdate_to_datetime(date_string, timezone_name):
    if not date_string:  # Check if the string is empty
        return None  # Return None if the string is empty
    if not timezone_name:
        timezone_name = 'Europe/Warsaw'

    # Define the format of the input date string with an optional timezone offset
    format_string_with_fractions = "%Y-%m-%dT%H:%M:%S.%f%z"
    format_string_without_fractions = "%Y-%m-%dT%H:%M:%S%z"

    try:
        # Try parsing with timezone offset including milliseconds
        datetime_object = datetime.strptime(date_string, format_string_with_fractions)
    except ValueError:
        try:
            # Try parsing with timezone offset without milliseconds
            datetime_object = datetime.strptime(date_string, format_string_without_fractions)
        except ValueError:
            raise ValueError("Invalid date format")

    # Extract the timezone offset
    timezone_offset_hours = int(date_string[-5:-3])
    timezone_offset_minutes = int(date_string[-3:-1])
    timezone_offset = timedelta(hours=timezone_offset_hours, minutes=timezone_offset_minutes)

    # Convert the datetime object to the specified timezone
    utc_datetime = datetime_object - timezone_offset
    local_timezone = pytz.timezone(timezone_name)
    local_datetime = utc_datetime.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    # Remove the timezone information
    local_datetime = local_datetime.replace(tzinfo=None)

    return local_datetime


def check_key(obj, key_string):
    return_string = ''
    try:
        return_string = obj[key_string]
    except KeyError:
        return_string = None
    return return_string
