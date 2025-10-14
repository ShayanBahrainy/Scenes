import resend
import os
import secrets
import string
from jinja2 import Environment, FileSystemLoader
import datetime

def get_time() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp())

resend.api_key = os.environ.get('RESEND_API_KEY')

EMAIL_CONFIG = {
    "from" : os.environ.get("SCENERY_FROM_EMAIL")
}


env = Environment(loader=FileSystemLoader("email_templates"))

EMAIl_VERIFICATION_TEMPLATE = env.get_template("email_verification.html")

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

"""
em = EmailManager()
em.send_code("Shayan", "shayanbahrainy@gmail.com")
result = em.verify("vink@aurorii.com", "JSkk222(((dj)))")

if result.success:
    print("fuck succedded")
else:
    print(result.reason)
"""
