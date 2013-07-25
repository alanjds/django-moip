#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django_moip.html.redirector.signals import redirector_successful, redirector_failed


@require_GET
def redirector(request):
    """MoIP redirector"""
    redirect_to = request.session.get('moip_go_after_return_url')
    if redirect_to:
        redirector_successful.send(sender=request)
    else:
        # Fallback to standard "thank you" page
        redirect_to = 'lfs_thank_you'
        redirector_failed.send(sender=request)

    return redirect(redirect_to)
