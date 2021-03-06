import decimal
import random, string
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from . import db

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for
                     x in range(32))


class SharedMethods(object):

    @classmethod
    def get_all_records(cls):
        return db.session.query(cls).all()

    @classmethod
    def get_record_by_id(cls, id):
        return db.session.query(cls).filter_by(id=id).first()

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        d = {}
        for c in self.__table__.columns:
            # convert decimal to string
            value = getattr(self, c.name)
            if isinstance(value, decimal.Decimal):
                value = str(value)
            d[c.name] = value
        return d

    def update(self, content):
        for key, value in content.items():
            setattr(self, key, value)
        db.session.add(self)
        if not db.session.is_modified(self):
            return
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model, SharedMethods):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String, index=True, unique=True, nullable=False)
    picture = db.Column(db.String)
    requests = db.relationship('Request', backref=db.backref(
        'user'), lazy='dynamic', cascade="all, delete, delete-orphan")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """ we don't store the password directly, but we store its
        hash
        """
        self.hash_password(password)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

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

    @staticmethod
    def get_user_by_id(id):
        user = User.query.filter_by(id=id).first()
        if not user:
            return 'User not found'
        return user


class Request(db.Model, SharedMethods):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    meal_type = db.Column(db.String) # e.g. 'Pizza'
    location_string = db.Column(db.String)
    latitude = db.Column(db.Numeric)
    longitude = db.Column(db.Numeric)
    meal_time = db.Column(db.String) # e.g. 'breakfast'
    filled = db.Column(db.Boolean)
    proposals = db.relationship(
        'Proposal', backref=db.backref('request'), lazy='dynamic',
        cascade="all, delete, delete-orphan")


class Proposal(db.Model, SharedMethods):
    __tablename__ = 'proposals'
    id = db.Column(db.Integer, primary_key=True)
    user_proposed_to = db.Column(db.Integer, nullable=False)
    user_proposed_from = db.Column(db.Integer, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('requests.id'),
                           nullable=False)
    filled = db.Column(db.Boolean, default=False)


class Date(db.Model, SharedMethods):
    __tablename__ = 'dates'
    id = db.Column(db.Integer, primary_key=True)
    user_1 = db.Column(db.Integer)
    user_2 = db.Column(db.Integer)
    restaurant_name = db.Column(db.String)
    restaurant_address = db.Column(db.String)
    restaurant_picture = db.Column(db.String)
    meal_time = db.Column(db.String) # e.g. 'breakfast'