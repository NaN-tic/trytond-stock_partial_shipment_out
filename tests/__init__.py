# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.stock_partial_shipment_out.tests.test_stock_partial_shipment_out import suite
except ImportError:
    from .test_stock_partial_shipment_out import suite

__all__ = ['suite']
