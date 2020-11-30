# This file is part of the sale_direct Tryton module.
# Please see the COPYRIGHT and README.rst files at the top level of this
# package for full copyright notices, license terms and support information.
try:
    from trytond.modules.sale_direct.tests.test_sale_direct import suite
except ImportError:
    from .test_sale_direct import suite

__all__ = ['suite']
