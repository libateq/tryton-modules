from re import match
from sys import exit

IDENTIFIER_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'

module_name = '{{ cookiecutter.module_name }}'
if not match(IDENTIFIER_REGEX, module_name):
    print('ERROR: {module_name} is not a valid Tryton module name!'.format(
         module_name=module_name))
    exit(1)

package_name = '{{ cookiecutter.package_name }}'
if not match(IDENTIFIER_REGEX, package_name):
    print('ERROR: {package_name} is not a valid Python package name!'.format(
         package_name=package_name))
    exit(1)
