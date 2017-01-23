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
from app.external_apis import get_geocode_location, find_restaurant
from test_utils import create_user, create_request, create_proposal

from app.models import User, Request


class ExternalAPIsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_geocode_location(self):
        result = get_geocode_location('Amsterdam')
        self.assertEquals((52.3702157, 4.895167900000001), result)

    def test_find_restaurant(self):
        result = find_restaurant('lunch', 'amsterdam')
        self.assertEquals(len(result['restaurant_name']) > 0, True)


