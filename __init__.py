# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .shipment import *


def register():
    Pool.register(
        Move,
        ShipmentOut,
        module='stock_partial_shipment_out', type_='model')
