# -*- encoding: utf-8 -*-

import json
import uuid
import random
import requests
from sqlalchemy import func, desc, and_, select, cast, Text

from apps.dostuff import blueprint
from apps import db
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, current_app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from io import BytesIO
import os.path

# from apps.dostuff.forms import PlaylistForm, TagForm
from apps.home.models import *
from apps.dostuff.models import *
from apps.authentication.models import UserConfig

@blueprint.route('/')
@login_required
def do_stuff():
    # Initialize variables
    conditions = []
    tags_to_search = []
    contexts_to_search = []
    boolean_condition = True
    integer_condition = 10
    # due_date_condition = datetime.date(2024, 2, 28)  # Example due date condition

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


    return redirect(url_for('mytube_blueprint.mytube'))


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