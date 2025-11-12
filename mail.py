from flask import Flask
from jinja2 import Environment, FileSystemLoader
from models import db
from app import app
from enum import StrEnum
from accounts import Account, SubscriptionStatus
import resend
import os
import secrets
import string
import datetime
import threading
import time
import queue


def get_time() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp())

resend.api_key = os.environ.get('RESEND_API_KEY')

EMAIL_CONFIG = {
    "from" : os.environ.get("SCENERY_FROM_EMAIL")
}

env = Environment(loader=FileSystemLoader("email_templates"))

EMAIl_VERIFICATION_TEMPLATE = env.get_template("email_verification.html")
GROUP_EMAIl_TEMPLATE = env.get_template("group_email.html")

class EmailVerificationResult:
    def __init__(self, success: bool, email: str, reason: str):
        self.success = success
        self.email = email
        self.reason = reason

class EmailVerificationAttempt:
    def __init__(self, code: str, expiry: int, email: str):
        self.code = code
        self.expiry = expiry
        self.email = email
    def verify(self, code: str) -> EmailVerificationResult:
        time = get_time()
        if code == self.code and self.expiry >= time:
            return EmailVerificationResult(True, self.email, None)
        elif code != self.code:
            return EmailVerificationResult(False, None, "Invalid code.")
        elif code == self.code and self.expiry < time:
            return EmailVerificationResult(False, None, "Code expired")

class EmailManager:
    CODE_LENGTH = 9
    VERIFY_EXPIRY_MINS = 15
    def __init__(self, host: str):
        self.verification_attempts: dict[str, EmailVerificationAttempt] = {}
        self.host = host
    def send_email(self, destination: str, subject: str, html: str):
        email = EMAIL_CONFIG.copy()
        email["to"] = destination
        email["subject"] = subject
        email["html"] = html

        resend.Emails.send(email)

    def send_code(self, email: str):
        code = self.generate_code()
        attempt = EmailVerificationAttempt(code, get_time() + (EmailManager.VERIFY_EXPIRY_MINS * 60), email)
        self.verification_attempts[email] = attempt
        url = "http://" + self.host + "/login-code/?email_code="+code+"&email="+email
        self.send_email(email, "Verify your email!", EMAIl_VERIFICATION_TEMPLATE.render(code=code,expiry=EmailManager.VERIFY_EXPIRY_MINS, verify_url=url))

    def generate_code(self, length=CODE_LENGTH):
        alphabet = string.ascii_uppercase + string.digits
        code = ''
        for i in range(length):
            code += secrets.choice(alphabet)
        return code

    def verify(self, email: str, code: str) -> EmailVerificationResult:
        if email not in self.verification_attempts:
            return EmailVerificationResult(False, None, "Email not found.")
        return self.verification_attempts[email].verify(code)

class EmailAttemptStatus(StrEnum):
    NOT_ATTEMPTED = "not_attempted"
    SENT = "sent"
    FAILED = "failed"

class EmailStatus(StrEnum):
    OPEN = "open" #No emails have been queued yet
    QUEUED = "attempts_queued" #Emails have been queued and will be sent out
    CLOSED = "closed" #No open send attempts

class EmailSendAttempt(db.Model):
    __tablename__ = 'send_attempts'

    id = db.Column(db.Integer, primary_key=True)

    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'), nullable=False)
    email = db.relationship('Email', backref='send_attempts')

    recipient_email = db.Column(db.String(50), db.ForeignKey('accounts.email'), nullable=False)
    recipient = db.relationship('Account', backref='email_attempts')

    status = db.Column(db.Enum(EmailAttemptStatus.NOT_ATTEMPTED.value, EmailAttemptStatus.SENT.value, EmailAttemptStatus.FAILED.value, name="EmailAttemptStatus"), nullable=False)
    reattempt_time = db.Column(db.Integer)

    def __init__(self, email_id: int, recipient_email: str, status: str):
        self.email_id = email_id
        self.recipient_email = recipient_email
        self.status = status

class EmailAudience(StrEnum):
    ALL = "ALL"
    PLUS = "PLUS"
    FREE = "FREE"

class EmailSendManager(threading.Thread):
    def __init__(self, email_manager: EmailManager):
        super().__init__()
        self.send_queue = queue.Queue()
        self.email_manager = email_manager

    def run(self):
        context = app.app_context()

        while True:
            with context:
                email_id = self.send_queue.get()
                email = db.session.query(Email).filter(Email.id == email_id).one()

                assert email.status == EmailStatus.OPEN

                email.status = EmailStatus.QUEUED

                audience_list = Email.__get_audience__(email.audience)

                for email_adr in audience_list:
                    db.session.add(EmailSendAttempt(email.id, email_adr, EmailAttemptStatus.NOT_ATTEMPTED.value))

                self.queued_time = get_time()
                db.session.commit()

                unsent_attempt = db.session.query(EmailSendAttempt).filter(EmailSendAttempt.status == EmailAttemptStatus.NOT_ATTEMPTED.value).first()

                if unsent_attempt:
                    self.email_manager.send_email(unsent_attempt.recipient_email, unsent_attempt.email.title, GROUP_EMAIl_TEMPLATE.render(email=email))

            time.sleep(3)

class Email(db.Model):
    __tablename__ = 'emails'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    audience = db.Column(db.String(25), nullable=False)
    status = db.Column(db.Enum(EmailStatus.OPEN.value, EmailStatus.QUEUED.value, EmailStatus.CLOSED.value, name="EmailStatus"), nullable=False)
    opened_time = db.Column(db.Integer, nullable=False)
    queued_time = db.Column(db.Integer)
    closed_time = db.Column(db.Integer)

    def __init__(self, title: str, body: str, audience: str):
        self.title = title
        self.body = body
        self.audience = audience
        self.status = EmailStatus.OPEN
        self.opened_time = get_time()

    @staticmethod
    def __get_audience__(audience: EmailAudience=EmailAudience.ALL) -> list[str]:
        if audience == EmailAudience.ALL:
            return [account.email for account in db.session.query(Account).all()]
        if audience == EmailAudience.PLUS:
            return [account.email for account in db.session.query(Account).filter(Account.subscription_status == SubscriptionStatus.PLUS.value).all()]
        if audience == EmailAudience.FREE:
            return [account.email for account in db.session.query(Account).filter(Account.subscription_status == SubscriptionStatus.NONE.value).all()]

    def __repr__(self):
        return f"Email({self.title}, {self.body}, {self.status}, {self.opened_time})"

if __name__ == "__main__":
    context = app.app_context()

    with context:
        db.create_all()

        all_email = Email("Here is a test email!", "And now... a test body", EmailAudience.ALL)
        premium_email = Email("Here is a premium email!", "And now... a test body", EmailAudience.PLUS)
        free_email = Email("Here is a free email!", "And now... a test body", EmailAudience.FREE)

        db.session.add(all_email)
        db.session.add(premium_email)
        db.session.add(free_email)

        db.session.commit()

        input("Press enter to move to next phase...")

        all_email.send()

        input(all_email)

        premium_email.send()


        input(premium_email)

        free_email.send()

        print(free_email)




