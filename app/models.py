import random, string
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from . import db

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for
                     x in range(32))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String, index=True)
    picture = db.Column(db.String)
    requests = db.relationship('Request', backref='user', lazy='dynamic')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    #Add a method to verify auth tokens here
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user_id = data['id']
        return user_id

    #TODO: add picture (gravatar) and requests
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'username': self.username,
            'email': self.email
        }


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    meal_type = db.Column(db.String) # e.g. 'Pizza'
    location_string = db.Column(db.String)
    latitude = db.Column(db.Numeric)
    longitude = db.Column(db.Numeric)
    meal_time = db.Column(db.String) # e.g. 'breakfast'
    filled = db.Column(db.Boolean)
    proposals = db.relationship('Proposal', backref='request', lazy='dynamic')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_type': self.meal_type,
            'location_string': self.location_string,
            'latitude': str(self.latitude),
            'longitude': str(self.longitude),
            'meal_time': self.meal_time,
            'filled': self.filled,
        }


class Proposal(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    user_proposed_to = db.Column(db.Integer)
    user_proposed_from = db.Column(db.Integer)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'))
    filled = db.Column(db.Boolean)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_proposed_to': self.user_proposed_to,
            'user_proposed_from': self.user_proposed_from,
            'request_id': self.request_id,
            'filled': self.filled,
        }


class Date(db.Model):
    __tablename__ = 'dates'
    id = db.Column(db.Integer, primary_key=True)
    user_1 = db.Column(db.Integer)
    user_2 = db.Column(db.Integer)
    restaurant_name = db.Column(db.String)
    restaurant_address = db.Column(db.String)
    restaurant_picture = db.Column(db.String)
    meal_time = db.Column(db.String) # e.g. 'breakfast'