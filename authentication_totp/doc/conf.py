# Configuration file for the Sphinx Documentation.
# This file is part of the authentication_totp Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from datetime import date
from os import chdir
from os.path import join, dirname


def get_copyright(first_year, current_year, author):
    years = first_year
    if first_year != current_year:
        years = '{}-{}'.format(first_year, current_year)
    return '{}, {}'.format(years, author)


def get_setup_argument(arg):
    global _setup_arguments_cache
    try:
        return _setup_arguments_cache.get(arg, None)
    except NameError:
        _setup_arguments_cache = {}

    def mock_setup(**kwargs):
        global _setup_arguments_cache
        _setup_arguments_cache = kwargs
    import setuptools
    setuptools.setup = mock_setup

    chdir(join(dirname(__file__), '..'))
    setup_py = 'setup.py'
    with open(setup_py, 'r', encoding='utf-8') as file:
        exec(file.read(), {'__file__': setup_py})

    return _setup_arguments_cache.get(arg, None)


def get_version(release):
    second_point = release.find('.', release.find('.')+1)
    return release[:second_point]


# Project information
project = get_setup_argument('name')
author = get_setup_argument('author')
copyright = get_copyright(2020, date.today().year, author)
release = get_setup_argument('version')
version = get_version(release)

# General settings
extensions = []
exclude_patterns = []
language = None
master_doc = 'index'
pygments_style = None
source_suffix = {'.rst': 'restructuredtext'}
templates_path = []

# HTML output settings
html_static_path = []

# LaTeX output settings
latex_elements = {'papersize': 'a4paper'}
latex_documents = [
    (master_doc, project + '.tex', project, author, 'manual', False),
    ]

# Man page output settings
man_pages = [
    (master_doc, project.replace('-', ''), project, [author], 1),
    ]

# Texinfo output settings
texinfo_documents = [
    (master_doc, project, project, author, project,
     get_setup_argument('description'), 'Miscellaneous', False),
    ]

# Epub output settings
epub_title = project
epub_exclude_files = ['search.html']
