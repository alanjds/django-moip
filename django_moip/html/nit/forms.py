#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django_moip.html.forms import MoipHtmlBaseForm 
from django_moip.html.ipn.models import MoipNIT


class MoipNITForm(MoipHtmlBaseForm):
    """
    Form used to receive and record PayPal NIT notifications.
    
    PayPal NIT test tool:
    https://developer.paypal.com/us/cgi-bin/devscr?cmd=_tools-session
    """
    class Meta:
        model = MoipNIT

