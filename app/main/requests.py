from flask import request, jsonify
from flask_httpauth import HTTPBasicAuth

from app.external_apis import get_geocode_location
from . import main
from .. import db
from ..models import Request

auth = HTTPBasicAuth()


@main.route('/api/v1/requests', methods=['GET', 'POST'])
@auth.login_required
def requests_function():
    """ show all requests (GET) or create request (POST)
    :return: return JSON of all requests (GET) or new request (POST).
    """

    if request.method == 'GET':
        return get_all_requests()

    elif request.method == 'POST':
        return create_request()


def get_all_requests():
    """
    :return: show all open requests of others
    """
    user = g.user
    meal_requests = db.session.query(Request).filter(
        Request.user_id != user.id, Request.filled != True).all()
    if not meal_requests:
        return 'no open meal requests of others'
    else:
        return jsonify(requests=[r.serialize for r in meal_requests])


def create_request():
    content = request.get_json(force=True)
    location_string = content.get('location_string')
    if not location_string:
        return 'Location required'
    latitude, longitude = get_geocode_location(location_string)
    meal_request = Request(
        meal_type=content.get('meal_type'),
        location_string=location_string,
        latitude=latitude, longitude=longitude,
        meal_time=content.get('meal_time'),
        user_id=g.user.id,
        filled=content.get('filled'),)
    db.session.add(meal_request)
    db.session.commit()
    return jsonify(meal_request.serialize)


@main.route('/api/v1/requests/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def requests_id_function(id):
    """
    :param id: request id (int)
    :return: return JSON of requests (GET) or changed request (PUT) or
    message (DELETE)
    """
    meal_request = Request.get_record_by_id(id)

    if not meal_request:
        return 'Meal_request not found'

    if request.method == 'GET':
        return jsonify(meal_request.serialize)

    elif request.method == 'PUT':
        content = request.get_json(force=True)
        updated_meal_request = meal_request.update(content)

        if not updated_meal_request:
            return 'Nothing to update'

        return jsonify(updated_meal_request.serialize)

    elif request.method == 'DELETE':
        return delete_request(id)


def update_request(id):
    return 'update request'


def delete_request(id):
    return 'delete request'
