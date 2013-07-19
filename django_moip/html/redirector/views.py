#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.http import require_GET
from django_moip.html.pdt.models import MoipPDT
from django_moip.html.pdt.forms import MoipPDTForm
 
 
@require_GET
def pdt(request, item_check_callable=None, template="pdt/pdt.html", context=None):
    """Payment data transfer implementation: http://tinyurl.com/c9jjmw"""
    context = context or {}
    pdt_obj = None
    txn_id = request.GET.get('tx')
    failed = False
    if txn_id is not None:
        # If an existing transaction with the id tx exists: use it
        try:
            pdt_obj = MoipPDT.objects.get(txn_id=txn_id)
        except MoipPDT.DoesNotExist:
            # This is a new transaction so we continue processing PDT request
            pass
        
        if pdt_obj is None:
            form = MoipPDTForm(request.GET)
            if form.is_valid():
                try:
                    pdt_obj = form.save(commit=False)
                except Exception, e:
                    error = repr(e)
                    failed = True
            else:
                error = form.errors
                failed = True
            
            if failed:
                pdt_obj = MoipPDT()
                pdt_obj.set_flag("Invalid form. %s" % error)
            
            pdt_obj.initialize(request)
        
            if not failed:
                # The PDT object gets saved during verify
                pdt_obj.verify(item_check_callable)
    else:
        pass # we ignore any PDT requests that don't have a transaction id
 
    context.update({"failed":failed, "pdt_obj":pdt_obj})
    return render_to_response(template, context, RequestContext(request))