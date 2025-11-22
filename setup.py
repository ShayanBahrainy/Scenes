env_template = """
RESEND_API_KEY={RESEND_API_KEY}
SCENERY_FROM_EMAIL={SCENERY_FROM_EMAIL}
STRIPE_KEY={STRIPE_KEY}
SCENERY_PLUS_ID={SCENERY_PLUS_ID}
SCENERY_ADMIN_EMAIL={SCENERY_ADMIN_EMAIL}
SCENERY_DB_URI={SCENERY_DB_URI}
"""


resend_api_key = input("Resend API Key: ")
scenery_from_email = input("What email do you want outgoing mail to be sent from: ")
stripe_key = input("Stripe API Key: ")
scenery_plus_id = input("Price id of the subscription (Found in Stripe Dashboard): ")
scenery_admin_email = input("Admin email: ")
scenery_db_uri = input("Database URI: ")


with open(".env", "w") as f:
    f.write(env_template.format(RESEND_API_KEY=resend_api_key, SCENERY_FROM_EMAIL=scenery_from_email, STRIPE_KEY=stripe_key, SCENERY_PLUS_ID=scenery_plus_id, SCENERY_ADMIN_EMAIL=scenery_admin_email, SCENERY_DB_URI=scenery_db_uri))

print("Environment has been configured!\nExiting...")