import httplib2, requests, json

from flask import request, make_response, json, jsonify, \
    g, abort, current_app
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from flask_httpauth import HTTPBasicAuth

from . import main
from .. import db
from ..models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    """ verification of token or username & password
    :return: returns true for valid user credentials
    """
    print('enter verify token')
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


# @main.route('/api/v1/clientOAuth')
# def start():
#     """
#     :return: generate one-time auth-code.
#     """
#     return render_template('clientOAuth.html')


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
    print('enter login')
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
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
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


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
