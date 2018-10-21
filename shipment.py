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
                'clear_unassigned': {
                    'invisible': Eval('state') != 'waiting',
                    'icon': 'tryton-go-jump',
                    },
                })

    @classmethod
    def clear_unassigned(cls, shipments):
        pool = Pool()
        Move = pool.get('stock.move')
        Uom = pool.get('product.uom')
        for shipment in shipments:
            assigned = {}
            to_delete = []
            for move in shipment.inventory_moves:
                if move.state == 'assigned':
                    if not move.product in assigned:
                        assigned.setdefault(move.product, 0.0)
                    assigned[move.product] += move.internal_quantity
                elif move.state == 'draft':
                    to_delete.append(move)
            for move in shipment.outgoing_moves:
                qty = assigned.get(move.product, 0.0)
                if qty > 0.0:
                    if move.internal_quantity > qty:
                        move.quantity = Uom.compute_qty(
                            move.product.default_uom, qty, move.uom)
                        move.save()
                    assigned[move.product] -= move.internal_quantity
                else:
                    to_delete.append(move)

        if to_delete:
            Move.delete(to_delete)

