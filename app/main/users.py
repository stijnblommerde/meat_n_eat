from flask import request, make_response, jsonify
from flask_httpauth import HTTPBasicAuth

from . import main
from .. import db
from ..models import User

auth = HTTPBasicAuth()


@main.route('/api/v1/users', methods=['GET', 'POST'])
@auth.login_required
def users_function():
    """ show all user (GET) or create user (POST)
    :return: return JSON of all users (GET) or new user (POST).
    """
    if request.method == 'GET':
        users = User.get_all_records()
        return jsonify(users=[user.serialize for user in users])
    elif request.method == 'POST':
        content = request.get_json(force=True)
        username = content.get('username')
        email = content.get('email')
        password = content.get('password')
        picture = content.get('picture')
        if not (username and password and email):
            return make_response('username, password and email required', 400)
        if db.session.query(User).filter_by(
                email=email).first():
            return make_response('user exists already', 400)
        user = User(username=username, email=email, password=password,
                    picture=picture)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.serialize)


@main.route('/api/v1/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def user_id_function(id):
    """
    :param id: user id (int)
    :return: return JSON of user (GET) or changed user (PUT) or
    message (DELETE)
    """
    user = User.get_record_by_id(id)

    if not user:
        return 'User not found'

    if request.method == 'GET':
        return jsonify(user.serialize)

    elif request.method == 'PUT':
        content = request.get_json(force=True)
        updated_user = user.update(content)

        if not updated_user:
            return 'Nothing to update'

        return jsonify(updated_user.serialize)

    elif request.method == 'DELETE':
        user.delete()
        return 'User has been deleted'
