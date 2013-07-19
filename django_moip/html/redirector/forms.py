#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django_moip.html.forms import MoipHtmlBaseForm
from django_moip.html.pdt.models import MoipPDT


class MoipPDTForm(MoipHtmlBaseForm):
    class Meta:
        model = MoipPDT