#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_GET
from django_moip.html.redirector.models import MoipRedirector
from django_moip.html.redirector.forms import MoipRedirectorForm
 
 
@require_GET
def redirector(request, item_check_callable=None, template="pdt/pdt.html", context=None):
    """MoIP redirector"""
    context = context or {}
    redirector_obj = None
    txn_id = request.GET.get('tx')
    failed = False
    if txn_id is not None:
        # If an existing transaction with the id tx exists: use it
        try:
            redirector_obj = MoipRedirector.objects.get(txn_id=txn_id)
        except MoipRedirector.DoesNotExist:
            # This is a new transaction so we continue processing Redirector request
            pass
        
        if redirector_obj is None:
            form = MoipRedirectorForm(request.GET)
            if form.is_valid():
                try:
                    redirector_obj = form.save(commit=False)
                except Exception, e:
                    error = repr(e)
                    failed = True
            else:
                error = form.errors
                failed = True
            
            if failed:
                redirector_obj = MoipRedirector()
                redirector_obj.set_flag("Invalid form. %s" % error)
            
            redirector_obj.initialize(request)
        
            if not failed:
                # The Redirector object gets saved during verify
                redirector_obj.verify(item_check_callable)
    else:
        pass # we ignore any Redirector requests that don't have a transaction id
 
    context.update({"failed":failed, "redirector_obj":redirector_obj})
    return render_to_response(template, context, RequestContext(request))