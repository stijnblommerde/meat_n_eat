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

    # def test_create_user(self):
    #     user_id = create_user('stijn', 'test')
    #     self.assertTrue(user_id)
    #
    # def test_create_request(self):
    #     # create user
    #     create_user('stijn', 'test')
    #     result = create_request('stijn', 'test')
    #     self.assertTrue(result)
    #
    # def test_get_all_requests(self):
    #
    #     # create self and other
    #     create_user('stijn', 'test')
    #     create_user('casper', 'test')
    #
    #     # create two requests by other, one filled and one open
    #     create_request('casper', 'test', False)
    #     create_request('casper', 'test', True)
    #
    #     # get all open meal requests by other
    #     try:
    #         h = Http()
    #         h.add_credentials(name='stijn', password='test')
    #         url = 'http://localhost:5000/api/v1/requests'
    #         resp, content_bytes = h.request(url, method='GET')
    #         if resp['status'] != '201' and resp['status'] != '200':
    #             raise Exception('Received an unsuccessful status code of %s' %
    #                             resp['status'])
    #         content = json.loads(content_bytes.decode())
    #
    #         # expected one meal request by user with id = 2
    #         self.assertTrue(len(content['requests']) == 1)
    #         self.assertTrue(content['requests'][0]['user_id'] == 2)
    #     except Exception as err:
    #         print(err)
    #         return None

    # def test_create_proposal(self):
    #     create_user('stijn', 'test')
    #     result = create_proposal('stijn', 'test')
    #     self.assertTrue(result)

    def test_get_all_proposals(self):
        """
        :return: show all proposals made by yourself and others
        """

        # create self and other
        user1_id = create_user('stijn', 'test')    # id = 1
        user2_id = create_user('casper', 'test')   # id = 2

        # others proposal on your request
        request1_id = create_request('stijn', 'test', False)
        proposal1_id = create_proposal('casper', 'test', request1_id, False)

        # your proposal on others request
        request2_id = create_request('casper', 'test', False)
        proposal2_id = create_proposal('stijn', 'test', request2_id, False)

        # get all open proposals (proposed meetups)
        try:
            h = Http()
            h.add_credentials(name='stijn', password='test')
            url = 'http://localhost:5000/api/v1/proposals'
            resp, content_bytes = h.request(url, method='GET')
            if resp['status'] != '201' and resp['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                resp['status'])
            content = json.loads(content_bytes.decode())

            # expected: one proposal from user 2
            self.assertTrue(len(content['proposals']) == 2, 'two proposals')
            self.assertTrue(content['proposals'][0]['user_id'] == 2,
                            'proposal 1 from user 2')
            self.assertTrue(content['proposals'][1]['user_id'] == 1,
                            'proposal 2 from user 1')
        except Exception as err:
            print(err)
            return None

    def test_create_date(self):
        """
        :return: accept proposal and create a meetup date
        """

