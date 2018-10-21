===========================
Stock Shipment Out Scenario
===========================

=============
General Setup
=============

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> today = datetime.date.today()

Activate stock_partial_shipment_out::

    >>> config = activate_modules('stock_partial_shipment_out')

Create company::

    >>> _ = create_company()
    >>> company = get_company()
    >>> party = company.party

Create customer::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('20')
    >>> template.cost_price = Decimal('8')
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])
    >>> output_loc, = Location.find([('code', '=', 'OUT')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])

Create Shipment Out::

    >>> ShipmentOut = Model.get('stock.shipment.out')
    >>> shipment_out = ShipmentOut()
    >>> shipment_out.planned_date = today
    >>> shipment_out.customer = customer
    >>> shipment_out.warehouse = warehouse_loc
    >>> shipment_out.company = company

Add two shipment lines of same product::

    >>> StockMove = Model.get('stock.move')
    >>> shipment_out.outgoing_moves.extend([StockMove(), StockMove()])
    >>> for move in shipment_out.outgoing_moves:
    ...     move.product = product
    ...     move.uom =unit
    ...     move.quantity = 1
    ...     move.from_location = output_loc
    ...     move.to_location = customer_loc
    ...     move.unit_price = Decimal('1')
    >>> shipment_out.save()

Set the shipment state to waiting::

    >>> ShipmentOut.wait([shipment_out.id], config.context)
    >>> shipment_out.reload()
    >>> len(shipment_out.outgoing_moves)
    2
    >>> len(shipment_out.inventory_moves)
    2

Make 1 unit of the product available::

    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 1
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.unit_price = Decimal('1')
    >>> incoming_move.save()
    >>> StockMove.do([incoming_move.id], config.context)

Assign the shipment now::

    >>> ShipmentOut.assign_try([shipment_out.id], config.context)
    False
    >>> shipment_out.reload()
    >>> len(shipment_out.outgoing_moves)
    2
    >>> len(shipment_out.inventory_moves)
    2
    >>> states = [m.state for m in shipment_out.inventory_moves]
    >>> states.sort()
    >>> states
    ['assigned', 'draft']

Clear unassigned moves, assign and pack shipment::

    >>> ShipmentOut.clear_unassigned([shipment_out.id], config.context)
    >>> shipment_out.reload()
    >>> len(shipment_out.outgoing_moves)
    1
    >>> len(shipment_out.inventory_moves)
    1
    >>> sum([m.quantity for m in shipment_out.inventory_moves]) == \
    ...     sum([m.quantity for m in shipment_out.outgoing_moves])
    True
    >>> ShipmentOut.assign_try([shipment_out.id], config.context)
    True
    >>> ShipmentOut.pack([shipment_out.id], config.context)
    >>> shipment_out.reload()
    >>> {m.state for m in shipment_out.outgoing_moves}
    {'assigned'}
    >>> shipment_out.inventory_moves[0].state
    'done'
    >>> sum([m.quantity for m in shipment_out.inventory_moves]) == \
    ...     sum([m.quantity for m in shipment_out.outgoing_moves])
    True
