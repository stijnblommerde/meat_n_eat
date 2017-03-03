from flask import Request
from flask import request, make_response, jsonify, g

from . import main
from .authentication import auth
from .. import db
from ..models import User

# TODO: finish experiment with overriding get_json
# class FlaskOverride(Request):
#
#     def __init__(self):
#         super(FlaskOverride, self).__init__(self)
#
#     def get_json(self, force=False, silent=False, cache=True):
#         print("override get_json")


@main.route('/api/v1/users/')
@auth.login_required
def get_all_users():
    """ Returns profile information off all users in the database.
    Only logged in users can view user profiles.
    :return: return JSON of all users in database
    """
    users = User.get_all_records()
    return jsonify(users=[user.serialize for user in users])


@main.route('/api/v1/users/', methods=['POST'])
def create_user():
    """ Creates a new user without using OAuth
    TODO: highly recommended to implement secure HTTP if this endpoint is
    implemented.
    As long as an email address isn’t in the database, create a new user,
    otherwise, return an appropriate error.
    :return: return details of new user in JSON format.
    """
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


@main.route('/api/v1/users/<int:id>')
@auth.login_required
def get_user(id):
    """
    :param id: user id (int)
    :return: return JSON of user
    """
    user = g.user
    if user.id != id:
        return jsonify(message='You can only view your own profile')
    return jsonify(user.serialize)


@main.route('/api/v1/users/<int:id>', methods=['PUT'])
@auth.login_required
def update_user(id):
    """ Updates a specific user’s information
    Server checks token to make sure only the logged in user can update her
    profile.
    :param id: user id (int)
    :return: return JSON of changed user
    """
    user = g.user
    if user.id != id:
        return jsonify(message='You can only change your own profile')
    content = request.get_json(force=True)
    # TODO: finish experiment with overriding get_json
    # fo = FlaskOverride()
    # content = fo.get_json(force=True)
    updated_user = user.update(content)
    if not updated_user:
        return 'Nothing to update'
    return jsonify(updated_user.serialize)


@main.route('/api/v1/users/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_user(id):
    """
    :param id: user id (int)
    :return: return message that the user has been deleted
    """
    user = g.user
    if user.id != id:
        return jsonify(message='You can only delete your own profile')
    user.delete()
    return jsonify(message='User has been deleted')