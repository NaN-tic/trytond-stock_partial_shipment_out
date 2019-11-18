# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['ShipmentOut']


class ShipmentOut(metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    @classmethod
    def __setup__(cls):
        super(ShipmentOut, cls).__setup__()
        cls._buttons.update({
                'partial_shipment': {
                    'invisible': Eval('state') != 'waiting',
                    'icon': 'tryton-clear',
                    },
                })

    @classmethod
    def partial_shipment(cls, shipments):
        Move = Pool().get('stock.move')

        to_delete = []
        for shipment in shipments:
            to_delete += [move for move in shipment.inventory_moves
                if move.state == 'draft']

        if to_delete:
            Move.delete(to_delete)
