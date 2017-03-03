import json
import unittest
from httplib2 import Http
from flask import current_app
from app import create_app, db


class UsersTestCase(unittest.TestCase):
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
        user_id = create_user('stijn', 'test', 'stijn@example.com')
        self.assertTrue(user_id)

    def test_get_all_users(self):
        create_user('stijn', 'test', 'stijn@example.com')
        h = Http()
        h.add_credentials(name='stijn', password='test')
        url = 'http://localhost:5000/api/v1/users'
        try:
            response, content_bytes = h.request(url, method='GET')
            if response['status'] != '201' and response['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                response['status'])
            content = json.loads(content_bytes.decode())
            self.assertTrue(content.get('users'))
        except Exception as e:
            self.assertTrue(False, 'Received an unsuccessful status code of %s' %
                                response['status'])

    def test_get_user(self):
        create_user('stijn', 'test', 'stijn@example.com')
        h = Http()
        h.add_credentials(name='stijn', password='test')
        url = 'http://localhost:5000/api/v1/users/1'
        try:
            response, content_bytes = h.request(url, method='GET')
            if response['status'] != '201' and response['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                response['status'])
            content = json.loads(content_bytes.decode())
            self.assertTrue(content.get('id'))
        except Exception as e:
            self.assertTrue(False,
                            'Received an unsuccessful status code of %s' %
                            response['status'])

    def test_change_user(self):
        create_user('stijn', 'test', 'stijn@example.com')
        h = Http()
        h.add_credentials(name='stijn', password='test')
        url = 'http://localhost:5000/api/v1/users/1'
        data = dict(username='casper', password='test2',
                    email='casper@example.com')
        try:
            response, content_bytes = h.request(
                url, method='PUT',
                body=json.dumps(data),
                headers={"Content-Type": "application/json"})
            if response['status'] != '201' and response['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                response['status'])
            content = json.loads(content_bytes.decode())
            self.assertEquals(content.get('username'), 'casper')
        except Exception as e:
            self.assertTrue(False,
                            'Received an unsuccessful status code of %s' %
                            response['status'])

    def test_delete_user(self):
        create_user('stijn', 'test', 'stijn@example.com')
        h = Http()
        h.add_credentials(name='stijn', password='test')
        url = 'http://localhost:5000/api/v1/users/1'
        try:
            response, content_bytes = h.request(url, method='DELETE')
            if response['status'] != '201' and response['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                                response['status'])
            content = json.loads(content_bytes.decode())
            self.assertEquals(content.get('message'), 'User has been deleted')
        except Exception as e:
            self.assertTrue(False,
                            'Received an unsuccessful status code of %s' %
                            response['status'])


def create_user(username, password, email):
    """ helper method that can be used to create users in test cases

    :return: user id
    """
    h = Http()
    url = 'http://localhost:5000/api/v1/users/'
    data = dict(username=username, password=password, email=email)
    try:
        response, content_bytes = h.request(
            url, method='POST',
            body=json.dumps(data),
            headers={"Content-Type": "application/json"})
        if response['status'] != '201' and response['status'] != '200':
            raise Exception('Received an unsuccessful status code of %s' %
                            response['status'])
        content = json.loads(content_bytes.decode())
        return content
    except Exception as err:
        print(err)
        return None