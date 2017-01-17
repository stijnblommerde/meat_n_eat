import unittest
import json
from httplib2 import Http
from flask import current_app
from app import create_app, db
from app.main.views import get_geocode_location
import sys
import string
import random


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
        try:
            resp, content = self.create_random_user()
            if resp['status'] != '201' and resp['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                resp['status'])
        except Exception:
            self.assertRaises(Exception)
        else:
            self.assertTrue(True)

    def test_get_user(self):
        try:
            h = Http()
            url = 'http://localhost:5000/api/v1/users/1'
            h.add_credentials(name="Peter", password="Pan")
            resp, content = h.request(url, 'GET')
            if resp['status'] != '201' and resp['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                resp['status'])
        except Exception:
            self.assertRaises(Exception)
        else:
            content = json.loads(content.decode())
            user = content.get('users')[0]
            self.assertEquals(user.get('username'), 'Peter')

    def test_create_request(self):
        try:
            resp, content = self.create_request()
            h.add_credentials(name="Peter", password="Pan")
            if resp['status'] != '201' and resp['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                resp['status'])
        except Exception:
            self.assertRaises(Exception)
        else:
            self.assertTrue(True)

    def test_create_proposal(self):
        request_id = self.create_request()
        print('enter test_create_proposal')
        print('request_id', request_id)
        print('type(request_id):', type(request_id))
        try:
            user1 = self.create_random_user()
            user2 = self.create_random_user()
            request_id = self.create_request()
            print('test')

            h = Http()
            url = 'http://localhost:5000/api/v1/proposals'
            resp, content = h.request(url, 'POST',
                      body=json.dumps(dict(
                          user_proposed_from=user1.id,
                          user_proposed_to=user2.id,
                          request_id=request_id,
                          filled=False,
                      )),
                      headers={"Content-Type": "application/json"})
            h.add_credentials(name="Peter", password="Pan")
            if resp['status'] != '201' and resp['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                resp['status'])
        except Exception:
            self.assertRaises(Exception)
        else:
            self.assertTrue(True)


    # helper functions

    def string_generator(size=5, chars=string.ascii_lowercase):
        return ''.join(random.choice(chars) for _ in range(size))

    def create_user(self):
        str1 = self.string_generator()
        str2 = self.string_generator()
        h = Http()
        url = 'http://localhost:5000/api/v1/users'
        data = dict(username=str1, password=str2)
        resp, content_bytes = h.request(url, 'POST',
                         body=json.dumps(data),
                         headers={"Content-Type": "application/json"})
        content = json.loads(content_bytes.decode())
        user = content.get('users')[0]
        return user

    def create_request(self):
        h = Http()
        url = 'http://localhost:5000/api/v1/requests'
        location_string = 'amsterdam'
        latitude, longitude = get_geocode_location(location_string)
        data = dict(meal_type='pizza',
                    location_string='amsterdam',
                    latitude=latitude,
                    longitude=longitude,
                    meal_time='lunch',
                    user_id=1,)
        resp, content_bytes = h.request(url, 'POST',
                         body=json.dumps(data),
                         headers={"Content-Type": "application/json"})
        content = json.loads(content_bytes.decode())
        request_id = content.get('request_id')[0]
        return request_id
