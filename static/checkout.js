// Initialize Stripe.js
const stripe = Stripe('pk_test_51SDG6Y6bitGFLr9YClPZAhv2oDIbpaJ6XTsWPa7B5oAbQ1vXFecCo2ZaJWOg195BB0rWSIybrXN7f73QJ2NPAIpM00RZDf8gxh');

initialize();

// Fetch Checkout Session and retrieve the client secret
async function initialize() {
  const fetchClientSecret = async () => {
    //Reuse secret if given.
    const params = new URLSearchParams(window.location.search)

    if (params.get('reuse_secret')) {
      return params.get('reuse_secret')
    }

    const response = await fetch("/create-checkout-session", {
      method: "POST",
    });

    if (!response.ok) {
        throw new Error("Failed to fetch the client secret.");
    }

    const { clientSecret } = await response.json();
    return clientSecret;
  };

  // Initialize Checkout
  const checkout = await stripe.initEmbeddedCheckout({
    fetchClientSecret,
  });

  // Mount Checkout
  checkout.mount('#checkout');
}
