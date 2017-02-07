'''
test requirements:
 - terminal tab 1: load test_vars.sh & start server (python manage.py runserver)
 - terminal tab 2: load test_vars.sh & run tests (python manage.py test)
'''

import json
import unittest
from flask import current_app
from httplib2 import Http

from app import create_app, db
from test_utils import create_user, create_request, create_proposal

from app.models import User, Request


class RequestTestCase(unittest.TestCase):

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

    def test_get_all_requests(self):

        # create self and other
        user1_id = create_user('stijn', 'test')
        user2_id = create_user('casper', 'test')

        # create two requests by other, one filled and one open
        create_request('casper', 'test', False)
        create_request('casper', 'test', True)

        # get all open meal requests by other
        try:
            h = Http()
            h.add_credentials(name='stijn', password='test')
            url = 'http://localhost:5000/api/v1/requests'
            resp, content_bytes = h.request(url, method='GET')
            if resp['status'] != '201' and resp['status'] != '200':
                raise Exception(
                    'Received an unsuccessful status code of %s' %
                    resp['status'])
            content = json.loads(content_bytes.decode())

            # expected one meal request by user with id = 2
            self.assertTrue(len(content['requests']) == 1)
            self.assertTrue(content['requests'][0]['user_id'] == user2_id)
        except Exception as err:
            print(err)
            return None






