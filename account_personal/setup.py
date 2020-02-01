#!/usr/bin/env python3
# This file is part of the account_personal Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# repository for full copyright notices, license terms and support information.
from io import open
from os.path import dirname, join
from setuptools import setup


def read(fname):
    with open(join(dirname(__file__), fname), 'r', encoding='utf-8') as file:
        return file.read()


setup(
    name='trytond_account_personal',
    version='5.4.1',
    description='Depreciated: Use trytonlq-account-personal instead.',
    long_description=read('README.rst'),
    author='David Harper',
    author_email='tryton@libateq.org',
    url='https://bitbucket.org/libateq/tryton-modules',
    project_urls={
        "Bug Tracker": 'https://bitbucket.org/libateq/tryton-modules/issues',
        "Source Code": 'https://bitbucket.org/libateq/tryton-modules',
        },
    keywords='tryton account personal',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        ],
    license='GPL-3',
    python_requires='>=3.5',
    install_requires=['trytonlq-account-personal >=5.4, <5.5'],
    zip_safe=False,
    )
