# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['ShipmentOut', 'Move']
__metaclass__ = PoolMeta


class ShipmentOut:
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

    def _get_inventory_move(self, move):
        # This method is duplicated from sale module
        # We need this method in case sale module is not installed
        new_move = super(ShipmentOut, self)._get_inventory_move(move)
        if new_move:
            new_move.origin = move
        return new_move

    @classmethod
    @ModelView.button
    def clear_unassigned(cls, shipments):
        pool = Pool()
        Move = pool.get('stock.move')
        Uom = pool.get('product.uom')

        for shipment in shipments:
            assigned = {} # assigned = {(product, move): quantity}
            to_delete = []

            for move in shipment.inventory_moves:
                if move.state == 'assigned':
                    if (move.product, move.origin) not in assigned:
                        assigned.setdefault(
                            (move.product, move.origin), 0.0)
                    assigned[(move.product, move.origin)] += move.internal_quantity
                elif move.state == 'draft':
                    to_delete.append(move)

            for move in shipment.outgoing_moves:
                qty = assigned.get((move.product, move), 0.0)
                if qty > 0.0:
                    if move.internal_quantity > qty:
                        move.quantity = Uom.compute_qty(
                            move.product.default_uom, qty, move.uom)
                        move.save()
                    assigned[(move.product, move)] -= move.internal_quantity
                else:
                    to_delete.append(move)

        if to_delete:
            Move.delete(to_delete)


class Move:
    __name__ = 'stock.move'

    @classmethod
    def _get_origin(cls):
        models = super(Move, cls)._get_origin()
        if not 'stock.move' in models:
            models.append('stock.move')
        return models
