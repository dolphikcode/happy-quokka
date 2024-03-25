# -*- encoding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'dostuff_blueprint',
    __name__,
    url_prefix='/todo'
)
