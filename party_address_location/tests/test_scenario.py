# This file is part of the party_address_location Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
from trytond.tests.test_tryton import load_doc_tests


def load_tests(*args, **kwargs):
    return load_doc_tests(__name__, __file__, *args, **kwargs)
