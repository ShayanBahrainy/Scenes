from flask import *
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename
from utils import get_time
from mail import EmailManager
from accounts import Account, Cookie, admin_auth
from payments import PaymentAccount, Payment
from streamer import Streamer
from models import db
from stripe_config import stripe
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://scenery:Scenery@localhost:5432/scenery'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'drafts/'

db.init_app(app)

HOST = os.environ.get("SCENERY_DOMAIN")
if not HOST:
    HOST = "127.0.0.1:5000"

emailmanager = EmailManager(HOST)

PREMIUM_QUALITIES = [Streamer.TEN_EIGHTY_P]

streamer = Streamer("test/", PREMIUM_QUALITIES)

SCENERY_PLUS_ID = os.environ.get("SCENERY_PLUS_ID")

ADMIN_EMAIL = os.environ.get("SCENERY_ADMIN_EMAIL")

STRIPE_ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET")
if not STRIPE_ENDPOINT_SECRET:
    STRIPE_ENDPOINT_SECRET = "whsec_5573f2cd2f99db84972c5971d7ad9afa3493d90610d026784ee3df5381b571c8"

@app.route("/")
def index(message=None):
    if "auth" in request.cookies:
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).first()
        if cookie:
            return render_template("index.html", user=cookie.user, message=message)
    return render_template("index.html", message=message)

@app.route("/login-start/", methods=["POST", "GET"])
def login_start():
    if request.method == "GET":
        return render_template("create_or_login.html")
    if request.method == "POST":
        email = request.form.get("email")
        if not email:
            return render_template("create_or_login.html", error="Please enter your email." if not email else None)
        emailmanager.send_code(email)
        return redirect("/login-code/")


@app.route("/login-code/", methods=["POST", "GET"])
def login_verify():
    if request.method == "GET":
        email_code = None
        email = None
        if "email_code" in request.args:
            email_code = request.args["email_code"]
        if "email" in request.args:
            email = request.args["email"]
        return render_template("verify_email.html", email_code=email_code, email=email)
    if request.method == "POST":
        code = request.form.get("code")
        email = request.form.get("email")
        if not code or not email:
            return render_template("verify_email.html", error="Please enter your email!" if not email else "Please enter your verification code!")
        verification = emailmanager.verify(email, code)
        if verification.success:
            account = db.session.query(Account).filter(Account.email == email).one_or_none()
            needs_setup = True if not account else account.name == None
            if not account:
                account = Account(email, 'none', get_time())
                db.session.add(account)
            cookie = Cookie(email)

            db.session.add(cookie)
            db.session.commit()

            response = redirect("/account_setup/" if needs_setup else "/")
            response.set_cookie("auth", cookie.cookie)
            return response
        return render_template("verify_email.html", error=verification.reason)

@app.route("/account_setup/", methods=["GET", "POST"])
def account_setup():
    if request.method == "GET":
        if "auth" not in request.cookies:
            return redirect("/login-start/")
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).first()
        if not cookie:
            response = redirect("/login-start/")
            response.delete_cookie("auth")
            return response
        if not cookie.user.name:
            return render_template("account_setup.html")
        return redirect("/", 302)
    if request.method == "POST":
        if "auth" not in request.cookies:
            return redirect("/login-start/")
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).first()
        if not cookie:
            response = redirect("/login-start/")
            response.delete_cookie("auth")
            return response
        name = request.form.get("name")
        if not name:
            return render_template("account_setup.html", error="Please include your name!")
        cookie.user.name = name
        db.session.commit()

        return index(message="Account setup complete!")

@app.route("/logout/")
def default_logout():
    return logout_route("here")

@app.route("/logout/<location>/")
def logout_route(location):
    response = redirect("/")
    if "auth" in request.cookies:
        this_cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if not this_cookie:
            return response
        if location == "here":
            db.session.delete(this_cookie)
            response.delete_cookie("auth")
        if location == "there":
            other_cookies = db.session.query(Cookie).filter(Cookie.email == this_cookie.email).filter(Cookie.cookie != this_cookie.cookie).all()
            for cookie in other_cookies:
                db.session.delete(cookie)
        if location == "everywhere":
            cookies = db.session.query(Cookie).filter(Cookie.email == this_cookie.email).filter(Cookie.cookie != this_cookie.cookie).all()
            for cookie in cookies:
                db.session.delete(cookie)
            response.delete_cookie("auth")
        db.session.commit()
    return response

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_api():
    if "auth" in request.cookies:
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if cookie:
            customer = db.session.query(PaymentAccount).filter(PaymentAccount.email == cookie.user.email, PaymentAccount.status == "open").one_or_none()
            session = stripe.checkout.Session.create(mode="subscription",
                line_items=[{"price": SCENERY_PLUS_ID, "quantity": 1}],
                ui_mode="embedded",
                return_url="http://" + HOST + "/checkout/return?session_id={CHECKOUT_SESSION_ID}",
                customer_email=cookie.user.email if not customer else None,
                customer=customer.stripe_id if customer else None,
            )
            return json.dumps({"clientSecret":session.client_secret})
    return Response("Not authenticated.", status=401)

@app.route("/reuse-checkout-session", methods=["GET"])
def reuse_checkout_api():
    if "auth" in request.cookies:
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if cookie:
            if "session" in request.args:
                session = stripe.checkout.Session.retrieve(request.args["session"])
                if session["customer_details"]["email"] == cookie.user.email:
                    return session.client_secret
    return Response("No matching session.", status=404)

@app.route("/create-portal-session", methods=["POST"])
def create_portal_api():
    if "auth" in request.cookies:
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if cookie:
            customer = db.session.query(PaymentAccount).filter(PaymentAccount.email == cookie.user.email, PaymentAccount.status == "open").one_or_none()
            if customer:
                session = stripe.billing_portal.Session.create(
                    customer=customer.stripe_id,
                    return_url="http://" + HOST + "/"
                )
                return redirect(session["url"])
            r = Response("User is not subscribed.")
            r.location = "http://" + HOST + "/subscribe"
            return r
    return Response("Not authenticated.", status=401)

@app.route("/subscribe")
def subscribe():
    if "auth" not in request.cookies:
        return redirect("/login-start")
    cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
    if not cookie:
        return redirect("/login-start")
    if cookie.user.subscription_status == 'plus':
        return redirect("/")
    return render_template("subscribe.html")

@app.route("/why-subscribe")
def why_subscribe():
    user = None
    if "auth" in request.cookies:
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if cookie:
            user = cookie.user
    return render_template("why_subscribe.html", user=user)

@app.route("/checkout/return")
def checkout_return():
    session_id = request.args.get('session_id')
    if not session_id:
        return redirect("/")
    checkout_session = stripe.checkout.Session.retrieve(session_id)
    return render_template("checkout_return.html", status=checkout_session.status)

@app.route("/stripe-event/", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_ENDPOINT_SECRET
        )
    except stripe.error.SignatureVerificationError as e:
        print('⚠️  Webhook signature verification failed.' + str(e))
        return jsonify(success=False)

    if event.type == "entitlements.active_entitlement_summary.updated":
        stripe_id = event.data.object.get("customer")
        payment_account = PaymentAccount.ensure_payment_account(stripe_id)
        entitlements = event.data.object["entitlements"]["data"]

        has_video = False
        for entitlement in entitlements:
            if entitlement["lookup_key"] == "full-quality-video":
                has_video = True
        payment_account.user.subscription_status = "plus" if has_video else "none"

    if event.type == "payment_intent.succeeded":
        stripe_id = event.data.object.get("customer")
        payment_account = PaymentAccount.ensure_payment_account(stripe_id)
        payment_object = event.data.object
        payment = Payment(payment_account.email, payment_object["amount"], payment_object["created"], "succeeded", stripe_id)
        db.session.add(payment)

    if event.type == "payment_intent.payment_failed":
        stripe_id = event.data.object.get("customer")
        payment_object = event.data.object
        payment_account = PaymentAccount.ensure_payment_account(stripe_id)
        payment = Payment(payment_account.email, payment_object["amount"], payment_object["created"], "failed", stripe_id)
        db.session.add(payment)

    if event.type == "customer.deleted":
        stripe_id = event.data.object.get("id")
        payment_account = db.session.query(PaymentAccount).filter(PaymentAccount.stripe_id == stripe_id).one_or_none()
        if payment_account:
            payment_account.status = "closed"

    db.session.commit()
    return jsonify(success=True)

@app.route("/scenery.m3u8")
def master_playlist():
    if "auth" not in request.cookies:
        return streamer.get_master_playlist()
    cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
    if not cookie:
        return streamer.get_master_playlist()
    if cookie.user.subscription_status != "plus":
        return streamer.get_master_playlist()
    return streamer.get_master_playlist(True)

@app.route("/<quality>.m3u8")
def get_playlist(quality):
    if quality not in streamer.playlists.keys():
        return make_response(f"No playlist with name '{quality}'", 404)

    if quality in PREMIUM_QUALITIES:
        if "auth" not in request.cookies:
            return make_response("Invalid authentication", 401)

        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if not cookie:
            return make_response("Invalid authentication", 401)

        if cookie.user.subscription_status != "plus":
            return make_response("Not authorized", 403)

    return streamer.get_media_playlist(quality)

@app.route("/test/<video_name>/<quality>/<file_name>.ts")
def return_video_file(video_name, quality, file_name):
    if quality in PREMIUM_QUALITIES:
        if "auth" not in request.cookies:
            return make_response("Invalid authentication", 401)

        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if not cookie:
            return make_response("Invalid authentication", 401)

        if cookie.user.subscription_status != "plus":
            return make_response("Not authorized", 403)

    path = safe_join(safe_join(video_name, quality), file_name+".ts")
    return send_from_directory('test/', path)

@app.route("/about-me")
def about_me():
    user = None
    if "auth" in request.cookies:
        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        user = cookie.user if cookie else None
    return render_template("about_me.html", user=user)

@app.route("/faq")
def faq_route():
    return render_template("faq.html")

@app.route("/admin/dashboard/")
def admin_dashboard():
    if admin_auth(request, ADMIN_EMAIL):
        num_accounts = db.session.query(Account).count()
        num_subscribers = db.session.query(Account).filter(Account.subscription_status == 'plus').count()
        #num_accounts = 50
        #num_subscribers = 25
        plus_price = stripe.Price.retrieve(SCENERY_PLUS_ID)["unit_amount"]
        return render_template("admin_dashboard.html", num_accounts=num_accounts, num_subscribers=num_subscribers, plus_price=plus_price)
    return abort(401)

@app.route("/admin/upload/", methods=["GET", "POST"])
def admin_upload():
    if not admin_auth(request, ADMIN_EMAIL):
        return abort(401)
    if request.method == "GET":
        return render_template("admin_upload.html")
    if request.method == "POST":
        file = request.files["video"]
        if not file.mimetype.startswith("video/"):
            return abort(400)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        return make_response("Draft created", status=201)

@app.route("/admin/videos/", methods=["GET", "PUT", "DELETE"])
def admin_viewall():
    if not admin_auth(request, ADMIN_EMAIL):
        return abort(401)
    if request.method == "GET":
        return render_template("admin_viewall.html")

@app.errorhandler(404)
def handle_404_error(e):
    return jsonify({
    "error": "Page not found",
    "message": "The resource you are looking for does not exist."
    }), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    streamer.start()
    app.run("0.0.0.0")