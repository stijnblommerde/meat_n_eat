from flask import request, jsonify, g
from sqlalchemy import or_

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
    user = g.user
    dates = db.session.query(Date).filter(or_(Date.user_1==user.id,
                                      Date.user_2==user.id)).all()
    return jsonify(dates=[d.serialize for d in dates])


@main.route('/api/v1/dates', methods=['POST'])
@auth.login_required
def create_date():
    """ Creates a new date request on behalf of a user
    If True, the recipient of a proposal has accepted this offer and is
    requesting that the server create a date.
    If false, the recipient of a proposal rejected a date and the proposal is
    deleted.
    After a date is created, the related request and proposal are filled
    :return:
    """
    user = g.user
    content = request.get_json(force=True)
    accept_proposal = content.get('accept_proposal')
    proposal_id = content.get('proposal_id')
    if accept_proposal is None or proposal_id is None:
        return jsonify(message="please provide proposal_id and accept_"
                               "proposal as a json string")
    proposal = db.session.query(Proposal).filter_by(
        id=proposal_id, user_proposed_to=user.id, filled=False).first()
    if not proposal:
        return jsonify(message="No open proposal found with the given "
                               "proposal id")
    if not accept_proposal:
        db.session.delete(proposal)
        db.session.commit()
        return jsonify(message="Recipient of proposal rejected a date and the "
                               "proposal is deleted")
    meal_request = db.session.query(Request).filter_by(
        id=proposal.request_id).first()
    restaurant = find_restaurant(meal_request.meal_type,
                                     meal_request.location_string)
    if not restaurant:
        return jsonify(message="No restaurant found")
    date = Date(
        user_1=user.id,
        user_2=proposal.user_proposed_from,
        restaurant_name=restaurant.get('restaurant_name'),
        restaurant_address=restaurant.get('address'),
        restaurant_picture=restaurant.get('image_url'),
        meal_time=meal_request.meal_time,)
    db.session.add(date)
    db.session.commit()
    # fill related request and proposal
    meal_request.update(filled=True)
    proposal.update(filled=True)
    return jsonify(date.serialize)


@main.route('/api/v1/dates/<int:id>')
@auth.login_required
def get_date(id):
    """ Gets information about a specific date
    Only dates where a user is a participant should appear in this view.
    :param id: date id (int)
    :return: return JSON of date
    """
    user = g.user
    date = Date.get_record_by_id(id)
    if not date:
        return jsonify(message="Date is not found")
    if not (user.id == date.user_1 or user.id == date.user_2):
        return jsonify(message="Only participants of can access this "
                               "information")
    return jsonify(date.serialize)


@main.route('/api/v1/dates/<int:id>', methods=['PUT'])
@auth.login_required
def update_date(id):
    """ Edits information about a specific date
    Only participants in the date can update the date details.
    :param id: proposal id (int)
    :return: return JSON of changed proposal
    """
    content = request.get_json(force=True)
    user = g.user
    date = db.session.query(Date).filter_by(id=id).first()
    if not date:
        return jsonify(message='Date not found')
    if not (user.id == date.user_1 or user.id == date.user_2):
        return jsonify(message="Only participants in the date can update the "
                               "date details.")
    updated_date = date.update(content)
    if not updated_date:
        return jsonify(message='Nothing to update')
    return jsonify(update_date.serialize)


@main.route('/api/v1/dates/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_date(id):
    """ Removes a specific date
    Only participants in the date can delete a date object.
    :param id: date id (int)
    :return: return JSON with message that date is deleted
    """
    user = g.user
    date = db.session.query(Proposal).filter_by(id=id).first()
    if not date:
        return 'Date not found'
    if not (user.id == date.user_1 or user.id == date.user_2):
        return jsonify(message="Only participants in the date can delete "
                               "a date object.")
    date.delete()
    return jsonify(message='Date deleted')