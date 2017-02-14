from flask import request, jsonify, g

from app.external_apis import get_geocode_location
from . import main
from .authentication import auth
from .. import db
from ..models import Request


@main.route('/api/v1/requests/', methods=['POST'])
@auth.login_required
def create_request():
    """ Makes a new meetup request
    Only logged in users can make meetup requests. The id of the maker of the
    request is stored in each request object.
    :return: return JSON of new request
    """
    content = request.get_json(force=True)
    location_string = content.get('location_string')
    if not location_string:
        return jsonify(message='Location required')
    latitude, longitude = get_geocode_location(location_string)
    meal_request = Request(
        user_id=g.user.id,
        meal_type=content.get('meal_type'),
        location_string=location_string,
        latitude=latitude,
        longitude=longitude,
        meal_time=content.get('meal_time'),
        filled=content.get('filled'))
    db.session.add(meal_request)
    db.session.commit()
    return jsonify(meal_request.serialize)


@main.route('/api/v1/requests/')
@auth.login_required
def get_all_requests():
    """ Shows all open meetup requests.
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
    """ show information for specific meetup request
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
    """ Updates information about a meetup request.
    Only the original maker of the request should be able to edit it.
    :param id: request id (int)
    :return: return JSON of changed request
    """
    user = g.user
    content = request.get_json(force=True)
    meal_request = Request.get_record_by_id(id)
    if not meal_request:
        return jsonify(message='Meal request not found')
    if user.id != meal_request.user_id:
        return jsonify(message='Only the original maker of the request can '
                               'edit it.')
    updated_meal_request = meal_request.update(content)
    if not updated_meal_request:
        return jsonify(message='Nothing to update')
    return jsonify(updated_meal_request.serialize)


@main.route('/api/v1/requests/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_request(id):
    """ delete request with given id
    Only the original maker of the request should be able to delete it.
    :param id: request id (int)
    :return: return JSON with message that request has been deleted
    """
    user = g.user
    meal_request = Request.get_record_by_id(id)
    if not meal_request:
        return jsonify(message='Meal request not found')
    if user.id != meal_request.user_id:
        return jsonify(message='Only the original maker of the request can '
                               'delete it.')
    meal_request.delete()
    return jsonify(message='Meal request has been deleted')