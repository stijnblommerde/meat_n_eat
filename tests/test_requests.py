import json
import unittest
from httplib2 import Http

from app import create_app, db
from tests.test_users import create_user
from app.models import User


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
    def test_create_request(self):
        create_user('stijn', 'test', 'stijn@example.com')
        result = create_request('stijn', 'test')
        self.assertTrue(result)

    def test_get_all_requests(self):
        create_user('stijn', 'test', 'stijn@example.com')

        # create one open and one filled meal request
        create_request('stijn', 'test', False)
        create_request('stijn', 'test', True)
        try:
            h = Http()
            h.add_credentials(name='stijn', password='test')
            url = 'http://localhost:5000/api/v1/requests/'
            response, content_bytes = h.request(url, method='GET')
            if response['status'] != '201' and response['status'] != '200':
                raise Exception('Received an unsuccessful status code of %s' %
                    response['status'])
            content = json.loads(content_bytes.decode())

            # expected one meal request
            self.assertTrue(len(content['requests']) == 1)
        except Exception as err:
            self.assertTrue(False,
                            'Received an unsuccessful status code of %s' %
                            response['status'])
        
    def test_get_request(self):
        user = create_user('stijn', 'test', 'stijn@example.com')
        request = create_request('stijn', 'test', False)
        try:
            h = Http()
            h.add_credentials(name='stijn', password='test')
            url = 'http://localhost:5000/api/v1/requests/%s' % request['id']
            response, content_bytes = h.request(url, method='GET')
            if response['status'] != '201' and response['status'] != '200':
                raise Exception(
                    'Received an unsuccessful status code of %s' %
                    response['status'])
            content = json.loads(content_bytes.decode())
            self.assertTrue(content.get('id'))
        except Exception as err:
            self.assertTrue(False,
                            'Received an unsuccessful status code of %s' %
                            response['status'])

    def test_update_request(self):
        user = create_user('stijn', 'test', 'stijn@example.com')
        request = create_request('stijn', 'test', False)
        try:
            h = Http()
            h.add_credentials(name='stijn', password='test')
            url = 'http://localhost:5000/api/v1/requests/%s' % request['id']
            data = dict(meal_type='pasta',
                        location_string='rotterdam',
                        meal_time='lunch',
                        user_id=user['id'],
                        filled=True)
            response, content_bytes = h.request(
                url, method='PUT',
                body=json.dumps(data),
                headers={"Content-Type": "application/json"})
            content = json.loads(content_bytes.decode())
            self.assertTrue(content.get('meal_type'), 'pasta')
        except Exception as err:
            self.assertTrue(False,
                            'Received an unsuccessful status code of %s' %
                            response['status'])

    def test_delete_request(self):
        user = create_user('stijn', 'test', 'stijn@example.com')
        request = create_request('stijn', 'test', False)
        self.assertTrue(request.get('id'))
        try:
            h = Http()
            h.add_credentials(name='stijn', password='test')
            url = 'http://localhost:5000/api/v1/requests/%s' % request['id']
            response, content_bytes = h.request(url, method='DELETE')
            content = json.loads(content_bytes.decode())
            self.assertFalse(content.get(request['id']))
        except Exception as err:
            self.assertTrue(False,
                            'Received an unsuccessful status code of %s' %
                            response['status'])
            

def create_request(username, password, filled=False):
    try:
        h = Http()
        user = db.session.query(User).filter_by(username=username).first()
        h.add_credentials(name=username, password=password)
        url = 'http://localhost:5000/api/v1/requests/'
        location_string = 'amsterdam'
        data = dict(meal_type='pizza',
                    location_string=location_string,
                    meal_time='lunch',
                    user_id=user.id,
                    filled=filled)
        response, content_bytes = h.request(
            url, method='POST',
            body=json.dumps(data),
            headers={"Content-Type": "application/json"})
        content = json.loads(content_bytes.decode())
        return content
    except Exception as err:
        return None




