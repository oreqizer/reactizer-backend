from uuid import uuid4
from flask import Blueprint, request, jsonify
from flask_babel import gettext
from sqlalchemy.exc import IntegrityError

from reactizer.database import db
from reactizer.models.user import User
from reactizer.models.refresh_token import RefreshToken
from reactizer.tools import auth

users = Blueprint('users', __name__)


@users.route('/api/users/login', methods=['POST'])
def login():
    """logs a user in.
    :returns the user info and user's token
    """
    payload = request.get_json()
    user = User.query.filter(User.username == payload['username']).first()
    if not user:
        return gettext('User not found.'), 401

    pw_hash = auth.hash_password(payload['password'], hashed=user['password'])
    if user['password'] != pw_hash:
        return gettext('Invalid password.'), 401

    app = payload['app']
    token = auth.get_token(user)
    refresh_token = RefreshToken.query.filter_by(app=app,
                                                 user_id=user.id).first()
    if not refresh_token:
        refresh_token = RefreshToken(user=user, app=app, token=uuid4())
        db.session.add(refresh_token)
        db.session.commit()

    return jsonify(user=user.for_user(),
                   token=token,
                   refresh_token=refresh_token.token)


@users.route('/api/users/refresh', methods=['POST'])
def refresh():
    """logs a user in using the refresh token.
    :returns the user info and user's token
    """
    token = request.get_json()['refresh_token']
    refresh_token = RefreshToken.query.filter_by(token=token).first()
    if not refresh_token:
        return gettext('User not found'), 401

    user = User.query.get(refresh_token.user_id)
    token = auth.get_token(user)
    return jsonify(user=user.for_user(),
                   token=token,
                   refresh_token=refresh_token.token)


@users.route('/api/users/register', methods=['POST'])
def register():
    """registers a new user.
    :returns the user info and user's token
    """
    payload = request.get_json()
    password = payload['password']
    # checks password validity
    try:
        auth.check_password(password)
    except ValueError as err:
        return str(err), 409

    payload['password'] = auth.hash_password(password)
    # guards if username/email are available
    try:
        user = User(**payload)
        db.session.add(user)
        db.session.commit()

        refresh_token = RefreshToken(user=user,
                                     app=payload['app'],
                                     token=uuid4())
        db.session.add(refresh_token)
        db.session.commit()

        token = auth.get_token(user)
        return jsonify(user=user.for_user(),
                       token=token,
                       refresh_token=refresh_token.token)
    except IntegrityError:
        return gettext('This username/email is taken.'), 409
