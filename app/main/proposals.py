import json

from flask import request, make_response, jsonify, g
from sqlalchemy import or_

from . import main
from .authentication import auth
from .. import db
from ..models import Proposal


@main.route('/api/v1/proposals')
@auth.login_required
def get_all_proposals():
    """ Retrieves all meetup proposals for a given user
    User is verified by the provided token and only corresponding proposals are
    returned if they are the maker or the recipient of a proposal.

    :return: return JSON of all proposals
    """
    user = g.user
    proposals = db.session.query(Proposal).filter(
        or_(Proposal.user_proposed_to == user.id,
            Proposal.user_proposed_from == user.id),
        Proposal.filled == False).all()
    if not proposals:
        return jsonify(message='No open proposals')
    return jsonify(proposals=[p.serialize for p in proposals])


@main.route('/api/v1/proposals', methods=['POST'])
@auth.login_required
def create_proposal():
    """ Creates a new proposal to meetup on behalf of a user
    User is verified by the provided token and identified as the maker of the
    proposal.

    :return: return JSON of new proposal
    """
    content = request.get_json(force=True)
    user_proposed_from = g.user.id
    user_proposed_to = content.get('user_proposed_to')
    if user_proposed_from == user_proposed_to:
        return make_response(json.dumps("Cannot make proposal to yourself."),
                             400)
    proposal = Proposal(user_proposed_to=user_proposed_to,
                 user_proposed_from=user_proposed_from,
                 request_id=content.get('request_id'),
                 filled=content.get('filled'))
    db.session.add(proposal)
    db.session.commit()
    return jsonify(proposal.serialize)


@main.route('/api/v1/proposals/<int:id>')
@auth.login_required
def get_proposal(id):
    """ Retrieves information about a specific proposal.
    he id of the user should match either the proposal maker or recipient in
    order to access this view.

    :param id: proposal id (int)
    :return: return JSON of proposals
    """
    user = g.user
    proposal = Proposal.get_record_by_id(id)
    if not proposal:
        return jsonify(message='Proposal not found')
    if not (user.id == proposal.user_proposed_from
            or user.id == proposal.user_proposed_to):
        return jsonify(message="Only proposal maker or recipient can access "
                               "this information")
    return jsonify(proposal.serialize)


@main.route('/api/v1/proposals/<int:id>', methods=['PUT'])
@auth.login_required
def update_proposal(id):
    """ Updates information about a specific proposal
    the id of the user should match the proposal maker in order to access this
    view.
    :param id: proposal id (int)
    :return: return JSON of changed proposal
    """
    content = request.get_json(force=True)
    user = g.user
    proposal = db.session.query(Proposal).filter_by(id=id).first()
    if not proposal:
        return jsonify(message='proposal not found')
    if not (user.id == proposal.user_proposed_from):
        return jsonify(message="Only proposal maker can access this "
                               "information")
    updated_proposal = proposal.update(content)
    if not updated_proposal:
        return jsonify(message='Nothing to update')
    return jsonify(updated_proposal.serialize)


@main.route('/api/v1/proposals/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_proposal(id):
    """ Deletes a specific proposal
    the id of the user should match the proposal maker in order to delete a
    proposal.
    :param id: proposal id (int)
    :return: return JSON with message that proposal is deleted
    """
    user = g.user
    proposal = db.session.query(Proposal).filter_by(id=id).first()
    if not proposal:
        return 'proposal not found'
    if not (user.id == proposal.user_proposed_from):
        return jsonify(message="Only proposal maker can access this "
                               "information")
    db.session.delete(proposal)
    db.session.commit()
    return jsonify(message='proposal deleted')