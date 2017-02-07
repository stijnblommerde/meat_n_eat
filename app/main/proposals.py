import json

from flask import request, make_response, jsonify
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import or_

from . import main
from .. import db
from ..models import Proposal

auth = HTTPBasicAuth()


@main.route('/api/v1/proposals', methods=['GET', 'POST'])
@auth.login_required
def proposals_function():
    """ show all proposals (GET) or create proposal (POST)
    :return: return JSON of all proposals (GET) or new proposal (POST).
    """
    if request.method == 'GET':
        return get_all_proposals()

    elif request.method == 'POST':
        return create_proposal()


def get_all_proposals():
    user = g.user
    proposals = db.session.query(Proposal).filter(
        or_(Proposal.user_proposed_to == user.id,
            Proposal.user_proposed_from == user.id),
        Proposal.filled).all()
    if not proposals:
        return 'no open proposals'
    return jsonify(proposals=[p.serialize for p in proposals])


def create_proposal():
    content = request.get_json(force=True)
    user_proposed_from = g.user.id
    user_proposed_to = content.get('user_proposed_to')
    if user_proposed_from == user_proposed_to:
        return make_response(json.dumps("Cannot make proposal to yourself."),
                             400)
    p = Proposal(user_proposed_to=user_proposed_to,
                 user_proposed_from=user_proposed_from,
                 request_id=content.get('request_id'),
                 filled=content.get('filled'))
    db.session.add(p)
    db.session.commit()
    return jsonify({'proposal_id': p.id})


@main.route('/api/v1/proposals/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def proposals_id_function(id):
    """
    :param id: proposal id (int)
    :return: return JSON of proposals (GET) or changed proposal (PUT) or
    message (DELETE)
    """
    proposal = Proposal.get_record_by_id(id)

    if not proposal:
        return 'Proposal not found'

    if request.method == 'GET':
        return jsonify(proposal.serialize)

    elif request.method == 'PUT':
        return update_proposal(id)

    elif request.method == 'DELETE':
        return delete_proposal(id)


def update_proposal(id):
    content = request.get_json(force=True)
    proposal = db.session.query(Proposal).filter_by(id=id).first()

    if not proposal:
        return 'proposal not found'

    if content.get('filled'):
        proposal.filled = True
        db.session.add(proposal)
        db.session.commit()

        # find restaurant

        date = create_date(
            # user_1=proposal.user_proposed_to,
            # user_2=proposal.user_proposed_from,
            # restaurant_name=,
        )

        return 'proposal accepted'

    return 'proposal not changed'


def delete_proposal(id):
    proposal = db.session.query(Proposal).filter_by(id=id).first()
    if not proposal:
        return 'proposal not found'
    db.session.delete(proposal)
    db.session.commit()
    return 'proposal deleted'