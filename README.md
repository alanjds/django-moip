Django MoIP
===========

CAUTION: ITS STILL BEING IMPLEMENTED. READ THE FOLLOW AS A BIG TODO-LIST!

About
-----

Django MoIP is a pluggable application that implements MoIP using HTML and API integrations.
It is based on the [django-paypal](https://github.com/dcramer/django-paypal) work
from John Boxall, David Cramer and Michael Thornhill (thank you!)


Using MoIP with the HTML integration + NIT
------------------------------------------

MoIP have an IPN (Instant Payment Notification), but it is called "NIT", from
Portuguese "Notificação Instantânea de Transação"

1. Download the code from GitHub:

        git clone git://github.com/alanjds/django-moip.git

1. Edit `settings.py` and add  `django_moip.html.nit` to your `INSTALLED_APPS` 
   and `MOIP_RECEIVER_EMAIL`:

        # settings.py
        ...
        INSTALLED_APPS = (... 'django_moip.integrations.html.nit', ...)
        ...
        MOIP_RECEIVER_EMAIL = "yourmoipemail@example.com.br"

1.  Create an instance of the `MoipPaymentForm` in the view where you would 
    like to collect money. Call `render` on the instance in your template to 
    write out the HTML.

        # views.py
        ...
        from django.conf import settings
        from django_moip.html.forms import MoipPaymentForm
        
        def view_that_asks_for_money(request):
        
            # What you want the button to do.
            moip_dict = {
                "id_carteira": settings.MOIP_RECEIVER_EMAIL,
                "valor": "%.0f" % (100 * 1234.0), # expects 2 decimal, no dot
                "nome": "name of the item",
                "id_transacao": "unique-invoice-id",
            }
            
            # Create the instance.
            form = MoipPaymentForm(initial=moip_dict)
            context = {"form": form}
            return render_to_response("payment.html", context)
            
            
        <!-- payment.html -->
        ...
        <h1>Show me the money!</h1>
        <!-- writes out the form tag automatically -->
        {{ form.render }}

    Note that MoIP HTML integration have no way to specify where to send the
    client after made the payment, so you need to manually set this
    http://www.example.com/your-return-location/ at MoIP admin dashboard,
    for example. (Shame...)

1.  When someone uses this form to buy something, MoIP makes a HTTP POST to
    your "notify_url". MoIP calls this "Notificação Instantânea de Transação" (NIT). 
    The view `django_moip.html.nit.views.nit` handles NIT processing. To set the 
    correct `notify_url` add the following to your `urls.py`:

        # urls.py
        ...
        urlpatterns = patterns('',
            (r'^something/hard/to/guess/', include('django_moip.html.nit.urls')),
        )

1.  Whenever an NIT is processed a signal will be sent with the result of the 
    transaction. Connect the signals to actions to perform the needed operations
    when a successful payment is recieved.
    
    There are two signals for basic transactions:
    - `payment_was_successful` 
    - `payment_was_flagged`

    MoIP is right now (2013.07) stabilizing its subscriptions and recurring
    payments. In the future, the following signals could be expected to exist:

    Four signals for subscriptions:
    - `subscription_cancel` - Sent when a subscription is cancelled.
    - `subscription_eot` - Sent when a subscription expires.
    - `subscription_modify` - Sent when a subscription is modified.
    - `subscription_signup` - Sent when a subscription is created.

    Several more for recurring payments:
    - `recurring_create` - Sent when a recurring payment is created.
    - `recurring_payment` - Sent when a payment is received from a recurring payment.
    - `recurring_cancel` - Sent when a recurring payment is cancelled.
    - `recurring_suspend` - Sent when a recurring payment is suspended.
    - `recurring_reactivate` - Sent when a recurring payment is reactivated.

    Connect to these signals and update your data accordingly. [Django Signals Documentation](http://docs.djangoproject.com/en/dev/topics/signals/).

        # models.py
        ...
        from django_moip.html.nit.signals import payment_was_successful
        
        def show_me_the_money(sender, **kwargs):
            nit_obj = sender
            # Undertake some action depending upon `nit_obj`.
            if nit_obj.custom == "Upgrade all users!":
                Users.objects.update(paid=True)
        payment_was_successful.connect(show_me_the_money)
        
        
Having the client back on your site
-----------------------------------

As MoIP have no equivalent of Paypal's PDT, you need to set an static URL that
your client will be redirected back in case of successfull payment, or if he
intentionaly desist after being denied.

You need to set this "return url" manually on MoIP admin dashboard. (Shame again)

To work around, django-moip allows you to set an session attribute
`moip_go_after_return_url`, and the provided 'return_redirector' will redirect
the visitor having this attribute set.

1. Download the code from GitHub:

        git clone git://github.com/alanjds/django-moip.git

1. Edit `settings.py` and add  `django_moip.html.redirector` to your `INSTALLED_APPS`.
   Just bewere that MoIP have no such thing as an "identity token", so you cannot
   rely on the call to say that the payment was successful.
   
   Bottomline: PLEASE, SET THE NIT AND BE SURE

        # settings.py
        ...
        INSTALLED_APPS = (... 'django_moip.html.redirector', ...)

1.  Create a view that uses `MoipPaymentForm` just like in MoIP NIT section.

1.  After someone uses this form to buy something, MoIP will return the user to your site at
    your "return_url" set on MoIP admin dashboard.
    The view `django_moip.html.redirector.views.return_redirector` handles the
    `moip_go_after_return_url` attribute on the visitor session. Please specify
    the correct `moip_go_after_return_url` on the session BEFORE showing the
    form to MoIP payment, and add the following to your `urls.py`:

        # urls.py
        ...
        urlpatterns = patterns('',
            (r'^moip/redirector/', include('django_moip.html.redirector.urls')),
            ...
        )


Using MoIP with the API integration
-----------------------------------

MoIP is, right now (2013.07), the only widespread national payment gateway that
provides serverside API payments, in the style of PayPal Pro API (WPP).

BUT they manually authorize every single account for this feature, and I am
trying to get this from some time, with no answer from its office. So,
no feature until I have a way to test it. Bad bad MoIP: no cookie for you!.

Links:
------

1. [Set your NIT Endpoint and "return url" on MoIP admin dashboard](https://www.moip.com.br/AdmCheckout.do?method=optional)

3. [MoIP HTML Integration Reference](https://www.moip.com.br/AdmCheckout.do?method=manual)


License (MIT)
=============

Copyright (c) 2013 Alan Justino da Silva

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
