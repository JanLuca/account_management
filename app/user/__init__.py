from flask import Blueprint, current_app
from flask_login import LoginManager
from flask_ldap3_login import LDAP3LoginManager

user_blueprint = Blueprint('user', __name__, template_folder='templates/')

from . import models, views

def init_app(app):

    login_manager = LoginManager(app)
    ldap_manager = LDAP3LoginManager(app)

    @ldap_manager.save_user
    def save_user(dn, username, data, memberships):
        user = models.User.from_ldap(dn=dn)
        return user

    @login_manager.user_loader
    def load_user(id):
        return models.User.from_ldap(dn=id)
