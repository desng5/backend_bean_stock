from app import db, login
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os, base64

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(75),nullable=False, unique=True)
    email = db.Column(db.String(75), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    coffees = db.relationship('Coffee', backref='brewer')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs['password'])

    def __repr__(self):
        return f"<User {self.id} | {self.username}>"

    def check_password(self, password_guess):
        return check_password_hash(self.password, password_guess)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.commit()
        return self.token

    def revoke_token(self):
        now = datetime.utcnow()
        self.token_expiration = now - timedelta(seconds=1)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

@login.user_loader
def get_user(user_id):
    return db.session.get(User, user_id)

class Coffee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    coffee_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(precision=6, scale=2), nullable=False)
    description = db.Column(db.String)
    rating = db.Column(db.Numeric(precision=2, scale=1))
    brew_method = db.Column(db.String(150))
    roaster = db.Column(db.String(50))
    image_url = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<Coffee {self.id} | {self.name} | {self.price}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'coffee_type': self.coffee_type,
            'price': self.price,
            'description': self.description,
            'rating': self.rating,
            'brew_method': self.brew_method,
            'roaster': self.roaster,
            'image_url': self.image_url,
            'date_created': self.date_created,
            'user_id': self.user_id
        }