# This file is part of the party_address_location Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.

trytond_url = 'https://docs.tryton.org/projects/server/en/{series}/'
modules_url = 'https://docs.tryton.org/projects/modules-{module}/en/{series}/'
modules_third_party_url = {}


def get_copyright(first_year, author):
    import datetime

    current_year = datetime.date.today().year
    if first_year == current_year:
        return '{}, {}'.format(first_year, author)
    return '{}-{}, {}'.format(first_year, current_year, author)


def get_info():
    import configparser
    import os
    import subprocess
    import sys

    module_dir = os.path.dirname(os.path.dirname(__file__))

    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(module_dir, 'tryton.cfg')))
    info = dict(config.items('tryton'))

    result = subprocess.run(
        [sys.executable, 'setup.py', '--name'],
        stdout=subprocess.PIPE, check=True, cwd=module_dir)
    info['name'] = result.stdout.decode('utf-8').strip()

    result = subprocess.run(
        [sys.executable, 'setup.py', '--author'],
        stdout=subprocess.PIPE, check=True, cwd=module_dir)
    info['author'] = result.stdout.decode('utf-8').strip()

    result = subprocess.run(
        [sys.executable, 'setup.py', '--version'],
        stdout=subprocess.PIPE, check=True, cwd=module_dir)
    version = result.stdout.decode('utf-8').strip()
    if 'dev' in version:
        info['series'] = 'latest'
    else:
        info['series'] = '.'.join(version.split('.', 2)[:2])

    for key in {'depends', 'extras_depend'}:
        info[key] = info.get(key, '').strip().splitlines()
    info['modules'] = set(info['depends'] + info['extras_depend'])
    info['modules'] -= {'ir', 'res'}

    return info


info = get_info()

project = info['name']
release = version = info['series']
author = info['author']
copyright = get_copyright(2021, author)
default_role = 'ref'
highlight_language = 'none'
extensions = [
    'sphinx.ext.intersphinx',
    ]
intersphinx_mapping = {
    'trytond': (trytond_url.format(series=version), None),
    }
intersphinx_mapping.update({
        m: (modules_url.format(
                module=m.replace('_', '-'), series=version), None)
        for m in info['modules']
        if m not in modules_third_party_url
        })
intersphinx_mapping.update({
        m: (modules_third_party_url[m].format(series=version), None)
        for m in info['modules']
        if m in modules_third_party_url
        })

del get_copyright, get_info, info
del modules_url, modules_third_party_url, trytond_url
