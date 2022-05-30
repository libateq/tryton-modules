#!/usr/bin/env python3
# This file is part of the {{ cookiecutter.module_name }} Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
import io
import os
import re
from configparser import ConfigParser

from setuptools import find_packages, setup

MODULE2PREFIX = {}


def read(fname):
    content = io.open(
        os.path.join(os.path.dirname(__file__), fname),
        'r', encoding='utf-8').read()
    content = re.sub(
        r'(?m)^\.\. toctree::\r?\n((^$|^\s.*$)\r?\n)*', '', content)
    return content


def get_require_version(name):
    if minor_version % 2:
        require = '%s >= %s.%s.dev0, < %s.%s'
    else:
        require = '%s >= %s.%s, < %s.%s'
    require %= (
        name, major_version, minor_version, major_version, minor_version + 1)
    return require


config = ConfigParser()
config.read_file(open(os.path.join(os.path.dirname(__file__), 'tryton.cfg')))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
version = info.get('version', '0.0.1')
major_version, minor_version, _ = version.split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)
name = '{{ cookiecutter.package_name }}'

if minor_version % 2:
    version = '%s.%s.dev0' % (major_version, minor_version)
local_version = []
if os.environ.get('CI_JOB_ID'):
    local_version.append(os.environ['CI_JOB_ID'])
else:
    for build in ['CI_BUILD_NUMBER', 'CI_JOB_NUMBER']:
        if os.environ.get(build):
            local_version.append(os.environ[build])
        else:
            local_version = []
            break
if local_version:
    version += '+' + '.'.join(local_version)

requires = []
for dep in info.get('depends', []):
    if not re.match(r'(ir|res)(\W|$)', dep):
        prefix = MODULE2PREFIX.get(dep, 'trytond')
        requires.append(get_require_version('%s_%s' % (prefix, dep)))
requires.append(get_require_version('trytond'))

{% if cookiecutter.test_with_scenario.lower().startswith('y') -%}
tests_require = [get_require_version('proteus')]
{%- else -%}
tests_require = []
{%- endif %}
dependency_links = []
if minor_version % 2:
    dependency_links.append(
        'https://trydevpi.tryton.org/?local_version='
        + '.'.join(local_version)
        + '&mirror=github')

setup(
    name=name,
    version=version,
    {% if cookiecutter.purpose|length <= 41 -%}
    description="Tryton module that {{ cookiecutter.purpose }}",
    {%- else -%}
    description=(
        {{ ('"Tryton module that ' + cookiecutter.purpose + '"') | wordwrap(width=69, wrapstring=' "\n        "')}}),
    {%- endif %}
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    author='{{ cookiecutter.tryton_package_author }}',
    author_email='{{ cookiecutter.tryton_package_email }}',
    url='{{ cookiecutter.tryton_modules_url }}',
    project_urls={
        "Bug Tracker": '{{ cookiecutter.tryton_modules_bugtracker_url }}',
        "Source Code": '{{ cookiecutter.tryton_modules_repository_url }}',
        },
    keywords='{{ cookiecutter.keywords }}',
    package_dir={'trytond.modules.{{ cookiecutter.module_name }}': '.'},
    packages=(
        ['trytond.modules.{{ cookiecutter.module_name }}']
        + ['trytond.modules.{{ cookiecutter.module_name }}.%s' % p
            for p in find_packages()]
        ),
    package_data={
        'trytond.modules.{{ cookiecutter.module_name }}': (
            info.get('xml', [])
            + ['tryton.cfg', 'view/*.xml', 'locale/*.po', '*.fodt',
                'icons/*.svg', 'tests/*.rst']),
        },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Office/Business',
        ],
    license='GPL-3',
    python_requires='>=3.7',
    install_requires=requires,
    extras_require={
        'test': tests_require,
        },
    dependency_links=dependency_links,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    {{ cookiecutter.module_name }} = trytond.modules.{{ cookiecutter.module_name }}
    {% if cookiecutter.module_name|length <= 28 -%}
    """,
    {%- else -%}
    """,  # noqa: E501
    {%- endif %}
    )
