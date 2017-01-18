import httplib2, requests, json

from flask import request, make_response, json, jsonify, \
    render_template, g, url_for, abort, redirect, current_app
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from flask_httpauth import HTTPBasicAuth

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


@main.route('/api/v1/users', methods=['POST'])
def create_user():
    content = request.get_json(force=True)
    username = content.get('username')
    password = content.get('password')
    if username is None or password is None:
        return make_response('username or password missing', 400)
    if db.session.query(User).filter_by(username=username).first() is not None:
        return make_response('user exists already', 400)
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'username': user.username}, 201)


@main.route('/api/v1/users', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def users_function():

    if request.method == 'GET':
        return get_all_users()

    elif request.method == 'PUT':
        return modify_user()

    elif request.method == 'DELETE':
        return delete_user()


def get_all_users():
    """
    :return: show all users in json format
    """
    users = db.session.query(User).all()
    return jsonify(users=[user.serialize for user in users])


def modify_user():
    return 'modify user'


def delete_user():
    return 'delete user'


@main.route('/api/v1/users/<int:id>')
@auth.login_required
def get_user(id):
    user = User.query.filter_by(id=id).first()
    if not user:
        return make_response('user not found', 400)
    return jsonify({'username': user.username})


@main.route('/api/v1/requests', methods=['GET', 'POST'])
@auth.login_required
def requests_function():

    if request.method == 'GET':
        return get_all_requests()

    elif request.method == 'POST':
        return create_request()


def get_all_requests():
    requests = db.session.query(Request).all()
    if not requests:
        return 'no open requests'
    else:
        return jsonify(requests=[r.serialize for r in requests])


def create_request():
    content = request.get_json(force=True)
    location_string = content.get('location_string')
    latitude, longitude = get_geocode_location(location_string)
    meal_request = Request(meal_type=content.get('meal_type'),
                location_string=location_string,
                latitude=latitude, longitude=longitude,
                meal_time=content.get('meal_time'), user_id=g.user.id)
    db.session.add(meal_request)
    db.session.commit()
    meal_request = db.session.query(Request).order_by(Request.id.desc()).first()
    return jsonify({'request_id': meal_request.id})


def get_geocode_location(location_string):
    """ Use Google Maps to convert a location into Latitute/Longitute coordinates

    FORMAT: https://maps.googleapis.com/maps/api/geocode/json?
    address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=API_KEY

    :param location_string:
    :return: latitude and longitude of location string
    """
    
    location_string = location_string.replace(" ", "+")
    url = (
        'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'%
        (location_string, current_app.config['GOOGLE_API_KEY']))
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1].decode('utf-8'))
    latitude = result['results'][0]['geometry']['location']['lat']
    longitude = result['results'][0]['geometry']['location']['lng']
    return latitude,longitude


@main.route('/api/v1/requests/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def requests_id(id):

    if request.method == 'GET':
        return get_request(id)

    elif request.method == 'PUT':
        return update_request(id)

    elif request.method == 'DELETE':
        return delete_request(id)


def get_request(id):
    return 'get single request'


def update_request(id):
    return 'update request'


def delete_request(id):
    return 'delete request'


@main.route('/api/v1/proposals', methods=['GET', 'POST'])
@auth.login_required
def proposals_function():

    if request.method == 'GET':
        return get_all_proposals()

    elif request.method == 'POST':
        return create_proposal()


def get_all_proposals():
    user = g.user
    proposals = db.session.query(Proposal).filter_by(user_proposed_to=user.id,
                                                     filled=False).all()
    if not proposals:
        return 'no open proposals'
    return jsonify(proposals=[p.serialize for p in proposals])


def create_proposal():
    print('enter create_proposal')
    content = request.get_json(force=True)
    user_proposed_from = int(g.user.id)
    user_proposed_to = int(content['user_proposed_to'])
    if user_proposed_from == user_proposed_to:
        return make_response(json.dumps("Cannot make proposal to yourself."),
                             400)
    p = Proposal(user_proposed_to=user_proposed_to,
                 user_proposed_from=user_proposed_from,
                 request_id=content['request_id'],
                 filled=False)
    db.session.add(p)
    db.session.commit()
    return jsonify({'proposal_id': p.id})


@main.route('/api/v1/proposals<int:id>', methods=['GET', 'PUT', 'DELETE'])
def proposals_id(id):

    if request.method == 'GET':
        return get_proposal(id)

    elif request.method == 'PUT':
        return update_proposal(id)

    elif request.method == 'DELETE':
        return delete_proposal(id)


def get_proposal(id):
    return 'get single proposal'


def update_proposal(id):
    return 'update single proposal'


def delete_proposal(id):
    return 'delete single proposal'


@main.route('/api/v1/dates', methods=['GET', 'POST'])
def dates():

    if request.method == 'GET':
        return get_dates()

    elif request.method == 'POST':
        return create_date()


@main.route('/api/v1/dates<int:id>', methods=['GET', 'PUT', 'DELETE'])
def get_date(id):

    if request.method == 'GET':
        return get_date(id)

    elif request.method == 'PUT':
        return update_date(id)

    elif request.method == 'DELETE':
        return delete_date(id)


def get_dates():
    return 'get all dates for user'


def create_date():
    return 'create date for user'


def get_date(id):
    return 'get single date'


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
