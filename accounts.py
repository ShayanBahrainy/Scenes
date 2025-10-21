import psycopg2
from flask_sqlalchemy import *
from flask import Request
import secrets
import string
from models import db
from enum import StrEnum

class SubscriptionStatus(StrEnum):
    NONE = 'none'
    PLUS = 'plus'


class Account(db.Model):
    __tablename__ = 'accounts'

    name = db.Column(db.String(50))
    email = db.Column(db.String(50), primary_key=True, unique=True)
    subscription_status = db.Column(db.Enum(SubscriptionStatus.NONE, SubscriptionStatus.PLUS, name="subscription"), nullable=False)
    signup_time = db.Column(db.Integer, nullable=False)

    def __init__(self, email: str, subscription_status: SubscriptionStatus, signup_time: int):
        self.email = email
        self.subscription_status = subscription_status
        self.signup_time = signup_time

    def __repr__(self):
        return f"Account({self.email}, {self.subscription_status}, {self.signup_time})"

class Cookie(db.Model):
    __tablename__ = 'cookies'
    cookie = db.Column(db.String(256), nullable=False, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('accounts.email'), nullable=False)
    user = db.relationship('Account', backref='cookies')

    def __init__(self, email: str):
        self.cookie = Cookie.generate_cookie()
        self.email = email

    @staticmethod
    def generate_cookie(length=256) -> str:
        cookie = ""
        options = string.ascii_letters + string.digits + "+/"
        for i in range(length):
            cookie += secrets.choice(options)
        return cookie

def admin_auth(request: Request, ADMIN_EMAIL: str):
    "Returns True if the request is authenticated as the admin."
    if "auth" in request.cookies:
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if cookie:
            if cookie.user.email == ADMIN_EMAIL:
                return True
    return False


