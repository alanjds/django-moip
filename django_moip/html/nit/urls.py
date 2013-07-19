from django.conf.urls.defaults import *

urlpatterns = patterns('django_moip.html.ipn.views',            
    url(r'^$', 'ipn', name="paypal-ipn"),
)