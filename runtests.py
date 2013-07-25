#coding: utf-8
# Don run this by itself. Instead, run "python setup.py test"
import sys
import getpass

from os.path import dirname, abspath

from django.conf import settings

if not settings.configured:
    settings.configure(
        ROOT_URLCONF='',
        DATABASE_ENGINE='sqlite3',
        MOIP_RECEIVER_EMAIL='test@example.com',
        MOIP_TEST=True,
        # Please dont make me create another test account and remove this from here :)
        INSTALLED_APPS=[
            'django_moip.html',
            'django_moip.html.nit',
            'django_moip.html.redirector',
        ]
    )

from discover_runner import DiscoverRunner
def run_tests(*args, **kwargs):
    runner = DiscoverRunner()
    return runner.run_tests(*args, **kwargs)


def runtests(*test_args):
    if not test_args:
        test_args = ['django_moip.html.nit', 'django_moip.html.redirector']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    failures = run_tests(test_args, verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
