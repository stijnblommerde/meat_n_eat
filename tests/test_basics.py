import unittest
import json
from httplib2 import Http
from flask import current_app
from app import create_app, db
from app.main.views import get_geocode_location
import sys
import string
import random

from app.models import User


class BasicsTestCase(unittest.TestCase):
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

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_create_user(self):
        result = self.create_user('stijn', 'test')
        self.assertTrue(result == {'username': 'stijn'})

    def create_user(self, username, password):
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
            user = content[0]
            return user
        except Exception as err:
            print(err)
            return None

    def test_create_request(self):
        result = self.create_request()
        self.assertTrue(result != None)

    def create_request(self):
        try:
            # create user
            self.create_user('stijn', 'test')
            user = db.session.query(User).filter_by(username='stijn').first()
            # create request
            h = Http()
            h.add_credentials(name='stijn', password='test')
            url = 'http://localhost:5000/api/v1/requests'
            location_string = 'amsterdam'
            data = dict(meal_type='pizza',
                        location_string=location_string,
                        meal_time='lunch',
                        user_id=user.id,
                        filled=False)
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

    def test_create_proposal(self):
        result = self.create_proposal()
        self.assertTrue(result != None)

    def create_proposal(self):
        try:
            # create users and request
            self.create_user('user1', 'password1')
            self.create_user('user2', 'password2')
            user1 = db.session.query(User).filter_by(username='user1').first()
            user2 = db.session.query(User).filter_by(username='user2').first()
            request_id = self.create_request()

            # create proposal
            h = Http()
            h.add_credentials(name='user1', password='password1')
            url = 'http://localhost:5000/api/v1/proposals'
            resp, content_bytes = h.request(
                url, method='POST',
                body=json.dumps(
                    dict(user_proposed_from=user1.id,
                         user_proposed_to=user2.id,
                         request_id=request_id,
                         filled=False,)),
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


