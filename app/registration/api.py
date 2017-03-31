from flask import request, abort, g
from flask.json import jsonify
from . import registration_blueprint, uni_token_required
from .models import Uni, Registration
from .helpers import send_registration_success_mail
from app.user import groups_required
from app.oauth2 import oauth
from app.db import db
import json

@registration_blueprint.route('/api/unis')
@oauth.require_oauth('uni_list')
def api_unis():
    unis = {uni.id: uni.name for uni in Uni.query.all()}
    return jsonify(unis)

@registration_blueprint.route('/api/registration', methods=['GET', 'POST'])
@oauth.require_oauth('registration')
def api_register():
    user = request.oauth.user
    registration = Registration.query.filter_by(username=user.username).first()
    if request.method == 'POST' \
        and request.headers.get('Content-Type') == 'application/json':
        req = request.get_json()
        if not registration:
            registration = Registration()

        registration.username = user.username
        registration.uni_id = req['uni_id']
        registration.blob = json.dumps(req['data'])
        # set registration to False on the first write
        registration.confirmed = registration.confirmed or False
        db.session.add(registration)
        db.session.commit()
        send_registration_success_mail(user)
        return "OK"

    if not registration:
        return "", 204

    return jsonify(
        uni_id = registration.uni_id,
        confirmed = registration.confirmed,
        data = registration.blob,
    )

@registration_blueprint.route('/api/priorities', methods=['GET', 'POST'])
@oauth.require_oauth('registration_priorities')
@uni_token_required
def api_registration_priorities():
    if request.method == 'POST' \
        and request.headers.get('Content-Type') == 'application/json':
        req = request.get_json()
        if not req:
            abort(403)
            return ''

        new_priority = len(req['priority'])

        registrations = Registration.query.filter_by(uni_id = g.uni.id)
        for registration in registrations:
            if registration.id in req['confirmed']:
                registration.confirmed = True
                # The try-catch block checks if the id of the 
                # registration is in the req['order'] list.
                # If found the index of the element in the list will be used
                # as priority of the registration.
                # If not found the registration will get the next free
                # priority as default value.
                try:
                    registration.priority = req['order'].index(reg_id)
                except ValueError:
                    registration.priority = new_priority
                    new_priority = new_priority + 1
            else:
                registration.confirmed = False
                registration.priority = None
            db.session.add(registration)

        db.session.commit()
        return "OK"

    registrations = Registration.query.filter_by(uni_id = g.uni.id).order_by(Registration.priority)
    confirmed = [
       {'reg_id': reg.id, 'name': reg.user.full_name, 'mail': reg.user.mail, 'priority': reg.priority}
       for reg in registrations if reg.confirmed
      ]
    not_confirmed = [     
       {'reg_id': reg.id, 'name': reg.user.full_name, 'mail': reg.user.mail, 'priority': reg.priority}
       for reg in registrations if not reg.confirmed
      ]

    return jsonify(confirmed = confirmed, not_confirmed = not_confirmed)
