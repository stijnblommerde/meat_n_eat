import httplib2, requests, json

from flask import request, make_response, json, jsonify, \
    render_template, g, url_for, abort, redirect, current_app
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import or_

from app.external_apis import get_geocode_location
from . import main
from .. import db
from ..models import User, Request, Proposal, Date

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    """ verification of token or username & password
    :return: returns true for valid user credentials
    """
    #Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = db.session.query(User).filter_by(id=user_id).one()
    else:
        user = db.session.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@main.route('/api/v1/clientOAuth')
def start():
    """
    :return: generate one-time auth-code.
    """
    return render_template('clientOAuth.html')


# @main.route('/token')
# @auth.login_required
# def get_auth_token():
#     token = g.user.generate_auth_token()
#     return jsonify({'token': token.decode('ascii')})


@main.route('/api/v1/<provider>/login', methods=['POST'])
def login(provider):
    """
    :param provider: oauth provider, e.g. Google or Facebook
    :return: send one-time oauth code and receive token
    """
    # step 1: parse the auth code
    # auth code is door user opgehaald bij google
    content = request.get_json(force=True)
    auth_code = content.get('auth_code')

    if provider == 'google':
        #step 2: exchange for a token
        try:
            #upgrade authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1].decode())
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        print("Step 2 Complete! Access Token : %s " % credentials.access_token)

        # STEP 3 - Find User or make a new one
        # Get user info from Google with API request
        url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(url, params=params)
        data = answer.json()
        name = data['name']
        picture = data['picture']
        email = data['email']

        # see if user exists, if it doesn't make a new one
        user = db.session.query(User).filter_by(email=email).first()
        if not user:
            user = User(username=name, picture=picture, email=email)
            db.session.add(user)
            db.session.commit()

        # STEP 4 - Make token
        token = user.generate_auth_token(600)

        # STEP 5 - Send back token to the client
        return jsonify({'token': token.decode('ascii')})

    else:
        return 'Unrecognized Provider'


# I chose not to implement logout route
# logout suggests storing data in a session
# RESTful APIs are stateless, they do not store information
# https://github.com/miguelgrinberg/Flask-HTTPAuth/issues/14
# @main.route('/api/v1/<provider>/logout')
# @auth.login_required
# def logout(provider):
#     return "logout"


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


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
