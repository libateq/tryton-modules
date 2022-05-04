#!/usr/bin/env python3
# This file is part of the {{ cookiecutter.module_name }} Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from configparser import ConfigParser
from io import open
from os.path import dirname, join
from re import match, sub
from setuptools import find_packages, setup


def setup_tryton_cfg():
    global tryton_cfg
    config = ConfigParser()
    with open('tryton.cfg') as config_file:
        config.read_file(config_file)
    tryton_cfg = dict(config.items('tryton'))
    for key in ('depends', 'extras_depend', 'xml'):
        if key in tryton_cfg:
            tryton_cfg[key] = tryton_cfg[key].strip().splitlines()


def setup_version():
    global version
    version = tryton_cfg.get('version', '0.0.1').split('.', 2)
    version = dict(
        zip(('major', 'minor', 'revision'), [int(i) for i in version]))
    if version['minor'] % 2:
        version['revision'] = 'dev{}'.format(version['revision'])


def read(fname):
    with open(join(dirname(__file__), fname), 'r', encoding='utf-8') as file:
        content = file.read()
    content = sub(
        r'(?m)^\.\. toctree::\r?\n((^$|^\s.*$)\r?\n)*', '', content)
    return content


def required_version(name, version):
    required = '{name} >={major}.{minor}{dev}, <{next_major}.{next_minor}'
    return required.format(
        name=name, next_major=version['major'], next_minor=version['minor']+1,
        dev='.dev0' if version['minor'] % 2 else '', **version)


def install_requires(third_party_packages={}):
    python_packages = []
    trytond_requires = [required_version('trytond', version)]
    for module in tryton_cfg.get('depends', []):
        if not match(r'(ir|res)(\W|$)', module):
            module_name = third_party_packages.get(
                module, 'trytond_{module}'.format(module=module))
            trytond_requires.append(required_version(module_name, version))
    return python_packages + trytond_requires


def tests_require():
    {% if cookiecutter.test_with_scenario.lower().startswith('y') -%}
    return [required_version('proteus', version)]
    {%- else -%}
    return []
    {%- endif %}


setup_tryton_cfg()
setup_version()
setup(
    name='{{ cookiecutter.package_name }}',
    version='{major}.{minor}.{revision}'.format(**version),
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
        ['trytond.modules.{{ cookiecutter.module_name }}'] +
        ['trytond.modules.{{ cookiecutter.module_name }}.{}'.format(p)
         for p in find_packages()]
        ),
    package_data={
        'trytond.modules.{{ cookiecutter.module_name }}': (
            tryton_cfg.get('xml', []) + [
                '*.fodt', 'icons/*.svg', 'locale/*.po', 'tests/*.rst',
                'tryton.cfg', 'view/*.xml']),
        },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Legal Industry',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa: E501
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Office/Business',
        ],
    license='GPL-3',
    python_requires='>=3.6',
    install_requires=install_requires(),
    extras_require={
        'test': tests_require,
        },
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
