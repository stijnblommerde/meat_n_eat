from flask import request, jsonify
from flask_httpauth import HTTPBasicAuth

from . import main
from .. import db
from ..models import Date

auth = HTTPBasicAuth()


@main.route('/api/v1/dates', methods=['GET', 'POST'])
def dates_function():
    """ show all dates (GET) or create date (POST)
    :return: return JSON of all dates (GET) or new date (POST).
    """
    if request.method == 'GET':
        return get_dates()

    elif request.method == 'POST':
        content = request.get_json(force=True)
        accept_proposal = content.get('accept_proposal')
        if accept_proposal:
            # TODO: add logic here
            pass
        return create_date()


@main.route('/api/v1/dates/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def date_id_function(id):
    """
    :param id: date id (int)
    :return: return JSON of dates (GET) or changed date (PUT) or
    message (DELETE)
    """
    date = Date.get_record_by_id(id)

    if not date:
        return 'Date not found'

    if request.method == 'GET':
        return jsonify(date.serialize)

    elif request.method == 'PUT':
        return update_date(id)

    elif request.method == 'DELETE':
        return delete_date(id)


def get_dates():
    return 'get all dates for user'


def create_date():
    # TODO: enter Date details
    date = Date()
    db.session.add(date)
    db.session.commit()
    return 'create date for user'


def update_date(id):
    return 'update date'


def delete_date(id):
    return 'delete date'