import stripe
import os


stripe.api_key = os.environ.get("STRIPE_KEY")

__all_ = ["stripe"]