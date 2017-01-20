import threading
import unittest
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from app import create_app, db
from app.models import User

chrome_options = Options()


class SeleniumTestCase(unittest.TestCase):
    driver = None

    @classmethod
    def setUpClass(cls):
        print('enter setupClass')
        # start Firefox
        try:
            #cls.driver = webdriver.Firefox()
            chrome_options.add_argument("user-data-dir=/Users/stijnblommerde/Library/Application Support/Google/Chrome/")
            cls.driver = webdriver.Chrome(chrome_options=chrome_options)
            #cls.driver = webdriver.Chrome()
            print('after cls.driver')
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.driver:
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
        if cls.driver:
            # stop the flask server and the browser
            cls.driver.get('http://localhost:5000/shutdown')
            cls.driver.quit()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application content
            cls.app_context.pop()

    def setUp(self):
        if not self.driver:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    # def test_start(self):
    #     # navigate to start page
    #     self.driver.get('http://localhost:5000/api/v1/clientOAuth')
    #     self.driver.find_element_by_id('signinButton').click()
    #     #TODO: unable to run signInCallback