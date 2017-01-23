import datetime
import os
from flask import json

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web'][
        'client_id'] # Google oauth
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY') # google geocode api
    print(GOOGLE_API_KEY)
    FOURSQUARE_CLIENT_ID = os.environ.get('FOURSQUARE_CLIENT_ID')
    FOURSQUARE_CLIENT_SECRET = os.environ.get('FOURSQUARE_CLIENT_SECRET')
    FOURSQUARE_VERSION = str(datetime.date.today()).replace('-', '')
    FOURSQUARE_INTENT = "browse"
    FOURSQUARE_RADIUS = "10000"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                                             'sqlite:///' + os.path.join(
                                                 basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    # disable CSRF tokens in tests
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig(),
    'default': DevelopmentConfig,
}