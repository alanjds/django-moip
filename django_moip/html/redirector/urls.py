from django.conf.urls.defaults import *

urlpatterns = patterns('django_moip.html.pdt.views',
    url(r'^$', 'pdt', name="paypal-pdt"),
)