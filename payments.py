from flask_sqlalchemy import SQLAlchemy
from models import db
from stripe_config import stripe

class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), db.ForeignKey('accounts.email'), nullable=False)
    stripe_id = db.Column(db.String(50), db.ForeignKey('payment_accounts.stripe_id'), nullable=False)
    payment_account = db.relationship('PaymentAccount', backref="payments")
    payment_amount = db.Column(db.Integer, nullable=False)
    payment_time = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.String(25), nullable=False)
    def __init__(self, email: str, payment_amount: int, payment_time: int, payment_status: str, stripe_id: str):
        self.email = email
        self.payment_amount = payment_amount
        self.payment_time = payment_time
        self.payment_status = payment_status
        self.stripe_id = stripe_id



class PaymentAccount(db.Model):
    __tablename__ = "payment_accounts"
    email = db.Column(db.String(50), db.ForeignKey('accounts.email'), nullable=False)
    stripe_id = db.Column(db.String(50), nullable=False, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    user = db.relationship('Account', backref='payment_accounts')
    def __init__(self, email: str, stripe_id: str):
        self.email = email
        self.stripe_id = stripe_id
        self.status = "open"

    @staticmethod
    def ensure_payment_account(stripe_id: str):
        payment_account = db.session.query(PaymentAccount).filter(stripe_id == PaymentAccount.stripe_id).one_or_none()
        if not payment_account:
            stripe_customer = stripe.Customer.retrieve(stripe_id)
            payment_account = PaymentAccount(stripe_customer["email"], stripe_id)
            db.session.add(payment_account)
        db.session.commit()
        return payment_account
