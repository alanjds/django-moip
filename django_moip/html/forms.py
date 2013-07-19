#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django_moip.html.conf import *
from django_moip.html.widgets import ValueHiddenInput, ReservedValueHiddenInput
from django_moip.html.conf import (POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT, 
    RECEIVER_EMAIL)


# 20:18:05 Jan 30, 2009 PST - PST timezone support is not included out of the box.
# MOIP_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST", "%H:%M:%S %b %d, %Y PST",)
# PayPal dates have been spotted in the wild with these formats, beware!
MOIP_DATE_FORMAT = ("%H:%M:%S %b. %d, %Y PST",
                      "%H:%M:%S %b. %d, %Y PDT",
                      "%H:%M:%S %b %d, %Y PST",
                      "%H:%M:%S %b %d, %Y PDT",)

class MoipPaymentsForm(forms.Form):
    """
    Creates a MoIP HTML Integration "Pay" button, configured for a
    selling a single item with no shipping.
    
    For a full overview of all the fields you can set (there is a lot!) see:
    https://www.moip.com.br/AdmCheckout.do?method=manual
    
    Usage:
    >>> f = MoipPaymentsForm(initial={'nome':'Widget 001', ...})
    >>> f.render()
    u'<form action="https://www.moip.com.br/PagamentoMoIP.do" method="post"> ...'
    
    """    
    SHIPPING_CHOICES = ((0, "No shipping"), (1, "Shipping"))
    NO_NOTE_CHOICES = ((1, "No Note"), (0, "Include Note"))
    RECURRING_PAYMENT_CHOICES = (
        (1, "Subscription Payments Recur"), 
        (0, "Subscription payments do not recur")
    )
    REATTEMPT_ON_FAIL_CHOICES = (
        (1, "reattempt billing on Failure"), 
        (0, "Do Not reattempt on failure")
    )

    BUY = 'buy'
    SUBSCRIBE = 'subscribe'
    DONATE = 'donate'

    # Where the money goes.
    business = forms.CharField(widget=ValueHiddenInput(), initial=RECEIVER_EMAIL)
    
    # Item information.
    amount = forms.IntegerField(widget=ValueHiddenInput())
    item_name = forms.CharField(widget=ValueHiddenInput())
    item_number = forms.CharField(widget=ValueHiddenInput())
    quantity = forms.CharField(widget=ValueHiddenInput())

    # NIT control.
    id_transacao = forms.CharField(widget=ValueHiddenInput())

    # Default fields.

    ## Optional fields
    frete = forms.ChoiceField(widget=forms.HiddenInput(), choices=SHIPPING_CHOICES, 
        initial=SHIPPING_CHOICES[0][0])

    def __init__(self, button_type="buy", *args, **kwargs):
        super(MoipPaymentsForm, self).__init__(*args, **kwargs)
        self.button_type = button_type

    def render(self):
        return mark_safe(u"""<form action="%s" method="post">
    %s
    <input type="image" src="%s" border="0" name="submit" alt="Buy it Now" />
</form>""" % (POSTBACK_ENDPOINT, self.as_p(), self.get_image()))
        
        
    def sandbox(self):
        return mark_safe(u"""<form action="%s" method="post">
    %s
    <input type="image" src="%s" border="0" name="submit" alt="Buy it Now" />
</form>""" % (SANDBOX_POSTBACK_ENDPOINT, self.as_p(), self.get_image()))
        
    def get_image(self):
        return {
            (True, self.SUBSCRIBE): SUBSCRIPTION_SANDBOX_IMAGE,
            (True, self.BUY): SANDBOX_IMAGE,
            (True, self.DONATE): DONATION_SANDBOX_IMAGE,
            (False, self.SUBSCRIBE): SUBSCRIPTION_IMAGE,
            (False, self.BUY): IMAGE,
            (False, self.DONATE): DONATION_IMAGE,
        }[TEST, self.button_type]

    def is_transaction(self):
        return not self.is_subscription()

    def is_donation(self):
        return self.button_type == self.DONATE

    def is_subscription(self):
        return self.button_type == self.SUBSCRIBE


class MoipEncryptedPaymentsForm(MoipPaymentsForm):
    """
    Creates a PayPal Encrypted Payments "Buy It Now" button.
    Requires the M2Crypto package.

    Based on example at:
    http://blog.mauveweb.co.uk/2007/10/10/paypal-with-django/
    
    """
    def _encrypt(self):
        """Use your key thing to encrypt things."""
        from M2Crypto import BIO, SMIME, X509
        # @@@ Could we move this to conf.py?
        CERT = settings.MOIP_PRIVATE_CERT
        PUB_CERT = settings.MOIP_PUBLIC_CERT
        MOIP_CERT = settings.MOIP_CERT
        CERT_ID = settings.MOIP_CERT_ID

        # Iterate through the fields and pull out the ones that have a value.
        plaintext = 'cert_id=%s\n' % CERT_ID
        for name, field in self.fields.iteritems():
            value = None
            if name in self.initial:
                value = self.initial[name]
            elif field.initial is not None:
                value = field.initial
            if value is not None:
                # @@@ Make this less hackish and put it in the widget.
                if name == "return_url":
                    name = "return"
                plaintext += u'%s=%s\n' % (name, value)
        plaintext = plaintext.encode('utf-8')
        
        # Begin crypto weirdness.
        s = SMIME.SMIME()
        s.load_key_bio(BIO.openfile(CERT), BIO.openfile(PUB_CERT))
        p7 = s.sign(BIO.MemoryBuffer(plaintext), flags=SMIME.PKCS7_BINARY)
        x509 = X509.load_cert_bio(BIO.openfile(settings.MOIP_CERT))
        sk = X509.X509_Stack()
        sk.push(x509)
        s.set_x509_stack(sk)
        s.set_cipher(SMIME.Cipher('des_ede3_cbc'))
        tmp = BIO.MemoryBuffer()
        p7.write_der(tmp)
        p7 = s.encrypt(tmp, flags=SMIME.PKCS7_BINARY)
        out = BIO.MemoryBuffer()
        p7.write(out)
        return out.read()
    
    def as_p(self):
        return mark_safe(u"""
<input type="hidden" name="cmd" value="_s-xclick" />
<input type="hidden" name="encrypted" value="%s" />
        """ % self._encrypt())


class MoipSharedSecretEncryptedPaymentsForm(MoipEncryptedPaymentsForm):
    """
    Creates a PayPal Encrypted Payments "Buy It Now" button with a Shared Secret.
    Shared secrets should only be used when your NIT endpoint is on HTTPS.
    
    Adds a secret to the notify_url based on the contents of the form.

    """
    def __init__(self, *args, **kwargs):
        "Make the secret from the form initial data and slip it into the form."
        from django_moip.html.helpers import make_secret
        super(MoipSharedSecretEncryptedPaymentsForm, self).__init__(*args, **kwargs)
        # @@@ Attach the secret parameter in a way that is safe for other query params.
        secret_param = "?secret=%s" % make_secret(self)
        # Initial data used in form construction overrides defaults
        if 'notify_url' in self.initial:
            self.initial['notify_url'] += secret_param
        else:
            self.fields['notify_url'].initial += secret_param


class MoipHtmlBaseForm(forms.ModelForm):
    """Form used to receive and record PayPal NIT/PDT."""
    # PayPal dates have non-standard formats.
    time_created = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
    payment_date = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
    next_payment_date = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
    subscr_date = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
    subscr_effective = forms.DateTimeField(required=False, input_formats=MOIP_DATE_FORMAT)
