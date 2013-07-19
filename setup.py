#!/usr/bin/env python

from setuptools import setup, find_packages

import django_moip

setup(
    name='django-moip',
    version=".".join(map(str, django_moip.__version__)),
    author='Alan Justino da Silva',
    author_email='alan.justino@yahoo.com.br',
    url='http://github.com/alanjds/django-moip',
    install_requires=[
        'Django>=1.0',
        'furl',
    ],
    tests_require = [
        'django-discover-runner'
    ],
    test_suite = 'runtests.runtests',
    description = 'A pluggable Django application for integrating MoIP HTML (for now)',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
