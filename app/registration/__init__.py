from flask import Blueprint, g, request
from flask_httpauth import HTTPTokenAuth
from functools import wraps

token_auth = HTTPTokenAuth(scheme='ZaPF-Token')
registration_blueprint = Blueprint('registration', __name__, template_folder='templates/')

def uni_token_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.headers.get('X-ZaPF-Token')
        if token:
            uni = models.Uni.query.filter_by(token=token).first()
            if uni is not None:
                g.uni = uni
                return f(*args, **kwargs)
        abort(403)
    return wrapped

from . import models, views

def init_app(app):
    return app
