from django.conf import settings

class MoipSettingsError(Exception):
    """Raised when settings be bad."""
    

TEST = getattr(settings, "MOIP_TEST", True)


RECEIVER_EMAIL = settings.MOIP_RECEIVER_EMAIL


# API Endpoints.
POSTBACK_ENDPOINT = "TODO https://www.paypal.com/cgi-bin/webscr"
SANDBOX_POSTBACK_ENDPOINT = "TODO https://www.sandbox.paypal.com/cgi-bin/webscr"

# Images
IMAGE = getattr(settings, "MOIP_IMAGE", "https://static.moip.com.br/imgs/buttons/bt_pagar_c01_e04.png")
SUBSCRIPTION_IMAGE = getattr(settings, "MOIP_SUBSCRIPTION_IMAGE", "TODO https://www.paypal.com/en_US/i/btn/btn_subscribeCC_LG.gif")
DONATION_IMAGE = getattr(settings, "MOIP_DONATION_IMAGE", "TODO https://www.paypal.com/en_US/i/btn/btn_donateCC_LG.gif")
SANDBOX_IMAGE = getattr(settings, "MOIP_SANDBOX_IMAGE", "https://static.moip.com.br/imgs/buttons/bt_pagar_c01_e04.png")
SUBSCRIPTION_SANDBOX_IMAGE = getattr(settings, "MOIP_SUBSCRIPTION_SANDBOX_IMAGE", "TODO https://www.sandbox.paypal.com/en_US/i/btn/btn_subscribeCC_LG.gif")
DONATION_SANDBOX_IMAGE = getattr(settings, "MOIP_DONATION_SANDBOX_IMAGE", "TODO https://www.sandbox.paypal.com/en_US/i/btn/btn_donateCC_LG.gif")

