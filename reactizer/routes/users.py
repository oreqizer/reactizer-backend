from flask import Blueprint, request, jsonify, g

from reactizer.database import db
from reactizer.models.users import User
from reactizer.tools import auth
from reactizer.enums.roles import Role

users = Blueprint('users', __name__)


@users.route('/api/users/<int:user_id>')
@auth.authorize(Role.user)
def show_user(user_id):
    """:returns the requested user"""
    if not g.user:
        return 'api.users.not_found', 404

    if g.user.id != user_id:
        return 'auth.not_owner', 401

    return jsonify(g.user.for_user())


@users.route('/api/users/login', methods=['POST'])
def login():
    """logs a user in.
    :returns the user info and user's token
    """
    payload = request.get_json()
    user = User.query.filter(User.username == payload['username']).first()
    if not user:
        return 'auth.user_not_found', 401

    pw_hash = auth.hash_password(payload['password'], hashed=user['password'])
    if user['password'] != pw_hash:
        return 'auth.invalid_password', 401

    token = auth.get_token(user)
    return jsonify(user=user.for_user(), token=token)


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
        return jsonify(status='error', msg=str(err))

    payload['password'] = auth.hash_password(password)
    # guards if username/email are available
    try:
        user = User(**payload)
        db.session.add(user)
        db.session.commit()
        token = auth.get_token(user)
        return jsonify(user=user.for_user(), token=token)
    except:
        return 'auth.integrity_taken', 409


# Admin routes
# ---


@users.route('/api/admin/users/<int:user_id>')
@auth.authorize(Role.admin)
def show_user_admin(user_id):
    """:returns the requested user for admin"""
    if not g.user:
        return 'api.users.not_found', 404

    if g.user.id != user_id:
        return 'auth.not_owner', 401

    return jsonify(g.user.for_user())


@users.route('/api/admin/users')
@auth.authorize(Role.admin)
def show_users_admin():
    """:returns all users"""
    results = [user.for_admin() for user in User.query.all()]
    return jsonify(users=results)