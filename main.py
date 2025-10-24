from flask import *
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename
import user_agents
from utils import get_time
from mail import Email, EmailManager, EmailStatus
from accounts import Account, Cookie, SubscriptionStatus, admin_auth
from payments import PaymentAccount, Payment
from streamer import Streamer
from models import db
from stripe_config import stripe
from video_processor import VideoProcessor, Video
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://scenery:Scenery@localhost:5432/scenery'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = 'uploaded/'

db.init_app(app)

HOST = os.environ.get("SCENERY_DOMAIN")
if not HOST:
    HOST = "127.0.0.1:5000"

emailmanager = EmailManager(HOST)

PREMIUM_QUALITIES = [Streamer.TEN_EIGHTY_P]


VIDEO_FOLDER = "videos/"
DRAFT_FOLDER = "drafts/"

streamer = Streamer(VIDEO_FOLDER, PREMIUM_QUALITIES)

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
            return render_template("index.html", user=cookie.user, message=message, is_admin=cookie.user.email==ADMIN_EMAIL)
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
                account = Account(email, SubscriptionStatus.NONE, get_time())
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
    if cookie.user.subscription_status == SubscriptionStatus.PLUS:
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
        payment_account.user.subscription_status = SubscriptionStatus.PLUS.value if has_video else SubscriptionStatus.NONE.value

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
    if cookie.user.subscription_status != SubscriptionStatus.PLUS:
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

        if cookie.user.subscription_status != SubscriptionStatus.PLUS:
            return make_response("Not authorized", 403)

    return streamer.get_media_playlist(quality)

@app.route("/videos/<video_name>/<quality>/<file_name>.ts")
def return_video_file(video_name, quality, file_name):
    if quality in PREMIUM_QUALITIES:
        if "auth" not in request.cookies:
            return make_response("Invalid authentication", 401)

        cookie = db.session.query(Cookie).filter(Cookie.cookie == request.cookies["auth"]).one_or_none()
        if not cookie:
            return make_response("Invalid authentication", 401)

        if cookie.user.subscription_status != SubscriptionStatus.PLUS:
            return make_response("Not authorized", 403)

    path = safe_join(safe_join(video_name, quality), file_name+".ts")
    return send_from_directory(VIDEO_FOLDER, path)

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
        num_subscribers = db.session.query(Account).filter(Account.subscription_status == SubscriptionStatus.PLUS).count()
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
        if '.' not in file.filename:
            return abort(400)
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        vid_name = filename.split('.')[0]
        processor = VideoProcessor(video_path=path, video_folder="uploaded/"+vid_name, move_path=os.path.join(DRAFT_FOLDER,vid_name))
        processor.start()
        return Response("Video processing", status=201)

@app.route("/admin/drafts/", methods=["GET", "PUT", "DELETE"])
def admin_view_drafts():
    if not admin_auth(request, ADMIN_EMAIL):
        return abort(401)
    user_agent = request.headers.get("User-Agent")
    parsed_useragent = user_agents.parse(user_agent)
    if request.method == "GET":
        video_drafts = []
        for video in os.listdir('drafts/'):
            draft = Video('/drafts/' + video + '/master.m3u8', video)
            video_drafts.append(draft)
        return render_template("admin_drafts.html", drafts=video_drafts, is_mobile=parsed_useragent.is_mobile)
    if request.method == "PUT":
        if "video_name" not in request.args:
            return abort(400)
        try:
            os.rename(os.path.join(DRAFT_FOLDER, request.args["video_name"]), os.path.join(VIDEO_FOLDER, request.args["video_name"]))
        except:
            return abort(400)
        return "Draft published"
    if request.method == "DELETE":
        if "video_name" not in request.args:
            return abort(400)
        try:
            os.remove(safe_join(DRAFT_FOLDER, request.args["video_name"]))
        except:
            return abort(400)
        return "Draft deleted"

@app.route("/admin/published/", methods=["GET", "PUT"])
def admin_published():
    if not admin_auth(request, ADMIN_EMAIL):
        return abort(401)
    user_agent = request.headers.get('User-Agent')
    parsed_useragent = user_agents.parse(user_agent)
    if request.method == "GET":
        VIDEOS_PER_PAGE = 10
        videos = []
        for folder in os.listdir(VIDEO_FOLDER):
            video = Video(os.path.join("/" + VIDEO_FOLDER, f"{folder}/master.m3u8"), video_name=folder)
            videos.append(video)
        page = request.args.get("page")
        if page:
            try:
                page = int(page)
            except:
                return abort(400)
        else:
            page = 0
        vid_per_page = VIDEOS_PER_PAGE
        if parsed_useragent.is_mobile:
            vid_per_page = 3
        page_count = (len(videos) + vid_per_page) // vid_per_page
        start = page * vid_per_page
        end = start + vid_per_page
        videos = videos[start:end]

        return render_template("admin_videos.html", videos=videos, page=page, page_count=page_count, is_mobile=parsed_useragent.is_mobile)

    if request.method == "PUT":
        if "video_name" not in request.args:
            return abort(400)
        try:
            os.rename(safe_join(VIDEO_FOLDER, request.args["video_name"]), safe_join(DRAFT_FOLDER, request.args["video_name"]))
        except:
            return abort(400)
        return "Video reverted to draft"

@app.route("/admin/email_dashboard/")
def email_dashboard():
    if not admin_auth(request, ADMIN_EMAIL):
        return abort(401)

    drafted_emails = db.session.query(Email).filter(Email.status != EmailStatus.CLOSED.value).all()

    return render_template("email_dashboard.html", drafted_emails=drafted_emails)

@app.route("/admin/email/edit/<email_id>", methods=["GET", "POST"])
def admin_email_edit(email_id):
    if not admin_auth(request, ADMIN_EMAIL):
        return abort(401)

    email = db.session.query(Email).filter(Email.id == email_id).one_or_none()

    if not email:
        return abort(400)

    if request.method == "GET":
        return render_template("emails.json", emails=[email])

    if request.method == "POST":
        if not request.is_json:
            return abort(400)

        if email.status != EmailStatus.OPEN:
            return Response("Email is not open.", status=400)

        data = request.get_json()

        if not data["title"] or not data["body"]:
            return Response("Required fields missing", status=400)

        email.title = data["title"]
        email.body = data["body"]

        db.session.commit()

        return "Email updated"

@app.route("/videos/<video_name>/<quality>/<filename>.m3u8")
def admin_return_playlist(video_name, quality, filename):
    if not admin_auth(request, ADMIN_EMAIL):
        return abort(401)
    playlist_path = safe_join(safe_join(safe_join("videos/", video_name), quality), filename+".m3u8")
    with open(playlist_path) as f:
        playlist = f.read()
    return Streamer.__add_basepath__(playlist, f"/videos/{video_name}/{quality}/")

@app.route("/<type>/<video_name>/master.m3u8")
def type_master(type, video_name):
    if not admin_auth(request, ADMIN_EMAIL):
        return abort(401)
    return Response(VideoProcessor.DRAFT_MASTER_TEMPLATE.format(video_folder_path=f"/{type}/"+video_name), mimetype="text/plain")

@app.route("/drafts/<video_name>/<quality>/<filename>", methods=["GET"])
def serve_draft(video_name, quality, filename):
    if admin_auth(request, ADMIN_EMAIL):
        path = safe_join(safe_join(safe_join("drafts/", video_name), quality), filename)
        return send_file(path)
    return abort(401)

@app.errorhandler(404)
def error_404(e):
    return Response(render_template("404.html"), status=404)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    streamer.start()
    app.run("0.0.0.0")