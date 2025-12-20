import subprocess

subprocess.run(["pip", "install", "-r", "requirements.txt"])

env_template = """
RESEND_API_KEY={RESEND_API_KEY}
SCENERY_FROM_EMAIL={SCENERY_FROM_EMAIL}
STRIPE_KEY={STRIPE_KEY}
SCENERY_PLUS_ID={SCENERY_PLUS_ID}
SCENERY_ADMIN_EMAIL={SCENERY_ADMIN_EMAIL}
SCENERY_DB_URI={SCENERY_DB_URI}
STRIPE_ENDPOINT_SECRET={STRIPE_ENDPOINT_SECRET}
VIDEO_FOLDER={VIDEO_FOLDER}
DRAFT_FOLDER={DRAFT_FOLDER}
"""

resend_api_key = input("Resend API Key: ")
scenery_from_email = input("\033[F\033[2KWhat email do you want outgoing mail to be sent from: ")
stripe_key = input("\033[F\033[2KStripe API Key: ")
scenery_plus_id = input("\033[F\033[2KPrice id of the subscription (Found in Stripe Dashboard): ")
scenery_admin_email = input("\033[F\033[2K Admin email: ")
scenery_db_uri = input("\033[F\033[2KDatabase URI: ")

stripe_webhook_secret = input("\033[F\033[2KWhat is your webhook secret: ")

ans = ""
while ans != "y" and ans != "n":
    ans = input("\033[F\033[2KDo you want to specify the video and draft folders (y/n): ")

video_folder = None
draft_folder = None

if ans == "y":
    video_folder = input("\033[F\033[2KEnter the path to the video folder: ")
    draft_folder = input("\033[F\033[2KEnter the path to the draft folder: ")

ans = ""
while ans != "y" and ans != "n":
    ans = input("\033[F\033[2KAre we running on a domain (y/n): ")

scenery_host = None
if ans == "y":
    scenery_host = input("\033[F\033[2KEnter the domain here:")

with open(".env", "w") as f:
    env = env_template.format(RESEND_API_KEY=resend_api_key, SCENERY_FROM_EMAIL=scenery_from_email, STRIPE_KEY=stripe_key, STRIPE_ENDPOINT_SECRET=stripe_webhook_secret, SCENERY_PLUS_ID=scenery_plus_id, SCENERY_ADMIN_EMAIL=scenery_admin_email, SCENERY_DB_URI=scenery_db_uri, VIDEO_FOLDER=video_folder, DRAFT_FOLDER=draft_folder)
    if video_folder:
        env += f"VIDEO_FOLDER={video_folder}\nDRAFT_FOLDER={draft_folder}\n"
    if scenery_host:
        env += f"SCENERY_DOMAIN={scenery_host}\n"
    f.write(env)

print("\033[F\033[2KEnvironment has been configured!\nExiting...")