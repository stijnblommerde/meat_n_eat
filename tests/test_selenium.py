import threading
import unittest
import time

from selenium import webdriver

from app import create_app, db
from app.models import User


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setupClass(cls):
        print('enter setupClass')
        # start Firefox
        try:
            cls.client = webdriver.Firefox()
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # create the database and populate with some fake data
            # TODO: populate with fake data
            db.create_all()

            # add a user
            user = User(username='user', password='password')
            db.session.add(user)
            db.session.commit()

            # start the Flask server in a thread
            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        print('enter teardownclass')
        if cls.client:
            # stop the flask server and the browser
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application content
            cls.app_context.pop()

    def setUp(self):
        self.setupClass()
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        self.tearDownClass()
        pass

    def test_start(self):
        # navigate to start page
        self.client.get('http://localhost:5000/api/v1/clientOAuth')
        self.client.find_element_by_id('signinButton').click()
        #time.sleep(3)
        self.client.switch_to.window("Sign in - Google Accounts")
        #TODO: add username and password as environmental vars for tests
        self.client.find_element_by_id('Email').send_keys('')
        time.sleep(3)
        print("result:", self.client.find_element_by_id('result').text)