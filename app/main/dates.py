from flask import request, jsonify

from app.external_apis import find_restaurant
from . import main
from .authentication import auth
from .. import db
from ..models import Date, Proposal, Request


@main.route('/api/v1/dates')
@auth.login_required
def get_all_dates():
    """ Gets all dates for a corresponding user
    Only the dates that contain the user id as one of the participants
    should be viewable by that user.
    :return:
    """
    return 'get all dates for user'


@main.route('/api/v1/dates', methods=['POST'])
@auth.login_required
def create_date():
    """ Creates a new date request on behalf of a user
    If True, the recipient of a proposal has accepted this offer and is
    requesting that the server create a date.
    If false, the recipient of a proposal rejected a date and the proposal is
    deleted.
    :return:
    """
    user = g.user
    content = request.get_json(force=True)
    proposal_id = content.get('proposal_id')
    proposal = db.session.query(Proposal).filter_by(
        id=proposal_id,
        user_proposed_to=user.id).first() # recipient of proposal
    meal_request = db.session.query(Request).filter_by(
        id=proposal.request_id).first()
    if not proposal:
        return jsonify(message="Proposal not found")
    accept_proposal = content.get('accept_proposal')
    if not accept_proposal:
        db.session.delete(proposal)
        db.session.commit()
        return jsonify(message="Recipient of proposal rejected a date and the "
                               "proposal is deleted")
    else:
        # TODO:find a local restaurant that matches the requested cuisine type
        # TODO:near the original proposer’s location
        restaurant = find_restaurant(meal_request.meal_type,
                                     meal_request.location_string)
    # TODO: add date params
    if not restaurant:
        return jsonify(message="No restaurant found")
    date = Date(
        user_1=user.id,
        user_2=proposal.user_proposed_from,
        restaurant_name=restaurant.get('restaurant_name'),
        restaurant_address=restaurant.get('address'),
        restaurant_picture=restaurant.get('image_url'),
        meal_time=meal_request.get('meal_time'),)
    db.session.add(date)
    db.session.commit()
    return jsonify(date.serialize)


@main.route('/api/v1/dates/<int:id>')
@auth.login_required
def get_date(id):
    """ Gets information about a specific date
    Only dates where a user is a participant should appear in this view.
    :param id:
    :return:
    """
    return 'get date'


@main.route('/api/v1/dates/<int:id>', methods=['PUT'])
@auth.login_required
def update_date(id):
    """ Edits information about a specific date
    Only participants in the date can update the date details.
    :param id:
    :return:
    """
    return 'update date'


@main.route('/api/v1/dates/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_date(id):
    """ Removes a specific date
    Only participants in the date can delete a date object.
    :param id:
    :return:
    """
    return 'delete date'