from flask import request, jsonify, g

from app.external_apis import get_geocode_location
from . import main
from .authentication import auth
from .. import db
from ..models import Request


@main.route('/api/v1/requests', methods=['POST'])
@auth.login_required
def create_request():
    """ create request
    :return: return JSON of new request
    """
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
        filled=content.get('filled'), )
    db.session.add(meal_request)
    db.session.commit()
    return jsonify(meal_request.serialize)


@main.route('/api/v1/requests')
@auth.login_required
def get_all_requests():
    """ show all open requests
    :return: return JSON of all requests
    """
    user = g.user
    meal_requests = db.session.query(Request).filter(
        Request.filled != True).all()
    if not meal_requests:
        return jsonify(message='No open meal requests')
    else:
        return jsonify(requests=[r.serialize for r in meal_requests])


@main.route('/api/v1/requests/<int:id>')
@auth.login_required
def get_request(id):
    """ show request with given id
    :param id: request id (int)
    :return: return JSON of request
    """
    meal_request = Request.get_record_by_id(id)
    if not meal_request:
        return jsonify(message='Meal request not found')
    return jsonify(meal_request.serialize)


@main.route('/api/v1/requests/<int:id>', methods=['PUT'])
@auth.login_required
def update_request(id):
    """ change request with given id
    :param id: request id (int)
    :return: return JSON of changed request
    """
    content = request.get_json(force=True)
    meal_request = Request.get_record_by_id(id)
    if not meal_request:
        return jsonify(message='Meal request not found')
    updated_meal_request = meal_request.update(content)
    if not updated_meal_request:
        return jsonify(message='Nothing to update')
    return jsonify(updated_meal_request.serialize)


@main.route('/api/v1/requests/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_request(id):
    """ delete request with given id
    :param id: request id (int)
    :return: return JSON with message that request has been deleted
    """
    meal_request = Request.get_record_by_id(id)
    if not meal_request:
        return jsonify(message='Meal request not found')
    meal_request.delete()
    return jsonify(message='Meal request has been deleted')