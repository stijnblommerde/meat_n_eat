import os
from flask import json

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web'][
        'client_id']
    GOOGLE_API_KEY = "AIzaSyCso6Rl-jJK3wv-chB0yOaHPKbZb9uJ-LA"

    @staticmethod
    def init_app():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                                             'sqlite:///' + os.path.join(
                                                 basedir, 'meat_n_eat.sqlite')


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
}