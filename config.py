import os
from flask import json

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web'][
        'client_id']
    GOOGLE_API_KEY = "AIzaSyCso6Rl-jJK3wv-chB0yOaHPKbZb9uJ-LA"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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