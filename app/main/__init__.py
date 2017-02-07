from flask import Blueprint

main = Blueprint('main', __name__)

from . import authentication, requests, proposals, dates, users, errors
