# -*- encoding: utf-8 -*-

import json
import uuid
import random

import pytz
import requests
from sqlalchemy import func, desc, and_, select, cast, Text

from apps.podtube import blueprint
from apps import db
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, current_app
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from io import BytesIO
import os.path

from apps.home.models import *
from apps.podtube.models import *
from apps.authentication.models import UserConfig


@blueprint.route('/')
@login_required
def podtube():
    pass
