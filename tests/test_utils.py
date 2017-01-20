from httplib2 import Http
import json
from app.models import User, Request
from app import db


def create_user(username, password):
    h = Http()
    url = 'http://localhost:5000/api/v1/users'
    data = dict(username=username, password=password)
    try:
        resp, content_bytes = h.request(
            url, method='POST',
            body=json.dumps(data),
            headers={"Content-Type": "application/json"})
        if resp['status'] != '201' and resp['status'] != '200':
            raise Exception('Received an unsuccessful status code of %s' %
                            resp['status'])
        content = json.loads(content_bytes.decode())
        user_id = content.get('user_id')
        return user_id
    except Exception as err:
        print(err)
        return None


def create_request(username, password, filled=False):
    try:
        h = Http()
        user = db.session.query(User).filter_by(username=username).first()
        h.add_credentials(name=username, password=password)
        url = 'http://localhost:5000/api/v1/requests'
        location_string = 'amsterdam'
        data = dict(meal_type='pizza',
                    location_string=location_string,
                    meal_time='lunch',
                    user_id=user.id,
                    filled=filled)
        resp, content_bytes = h.request(
            url, method='POST',
            body=json.dumps(data),
            headers={"Content-Type": "application/json"})
        content = json.loads(content_bytes.decode())
        request_id = content.get('request_id')
        return request_id
    except Exception as err:
        print(err)
        return None


def create_proposal(username, password, request_id, filled=False):
    try:
        h = Http()
        h.add_credentials(name=username, password=password)
        user_proposed_from_id = db.session.query(User).filter_by(
            username=username).first().id
        user_proposed_to_id = db.session.query(Request).filter_by(
            id=request_id).first().user_id
        url = 'http://localhost:5000/api/v1/proposals'
        data = dict(user_proposed_from=user_proposed_from_id,
                    user_proposed_to=user_proposed_to_id,
                    request_id=request_id,
                    filled=filled)
        resp, content_bytes = h.request(
            url, method='POST',
            body=json.dumps(data),
            headers={"Content-Type": "application/json"})
        if resp['status'] != '201' and resp['status'] != '200':
            raise Exception('Received an unsuccessful status code of %s' %
                            resp['status'])
        content = json.loads(content_bytes.decode())
        proposal_id = content.get('proposal_id')
        return proposal_id
    except Exception as err:
        print(err)
        return None

