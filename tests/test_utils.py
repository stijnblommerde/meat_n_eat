"""
test_utils are a bunch of methods to create test data.
these helper functions are tested as well to make sure that they work.

test requirements:
 - terminal tab 1: load test_vars.sh & start server (python manage.py runserver)
 - terminal tab 2: load test_vars.sh & run tests (python manage.py test)
"""

import json
import unittest
from flask import current_app
from httplib2 import Http

from app import create_app, db
from app.models import User, Request


class UtilsTestCase(unittest.TestCase):

    # boilerplate

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # tests

    def test_create_user(self):
        user_id = create_user('stijn', 'test')
        self.assertTrue(user_id)

    def test_create_proposal(self):
        create_user('stijn', 'test')
        result = create_proposal('stijn', 'test')
        self.assertTrue(result)

    def test_create_request(self):
        # create user
        create_user('stijn', 'test')
        result = create_request('stijn', 'test')
        self.assertTrue(result)

    def test_create_date(self):
        """
        :return: accept proposal and create a meetup date
        """
        pass


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


