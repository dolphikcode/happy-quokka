# -*- encoding: utf-8 -*-

from flask import Blueprint

blueprint = Blueprint(
    'shtf_blueprint',
    __name__,
    url_prefix='/shtf'
)
