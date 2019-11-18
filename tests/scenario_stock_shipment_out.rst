===========================
Stock Shipment Out Scenario
===========================

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
    >>> template = ProductTemplate()
    >>> template.name = 'Product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('20')
    >>> template.save()
    >>> product, = template.products
    >>> template2 = ProductTemplate()
    >>> template2.name = 'Product 2'
    >>> template2.default_uom = unit
    >>> template2.type = 'goods'
    >>> template2.list_price = Decimal('20')
    >>> template2.save()
    >>> product2, = template2.products

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> customer_loc, = Location.find([('code', '=', 'CUS')])
    >>> output_loc, = Location.find([('code', '=', 'OUT')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])

Make 1 unit of the product available::

    >>> StockMove = Model.get('stock.move')
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
    >>> incoming_move.click('do')

Make 10 unit of the product available::

    >>> incoming_move = StockMove()
    >>> incoming_move.product = product
    >>> incoming_move.uom = unit
    >>> incoming_move.quantity = 10
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = storage_loc
    >>> incoming_move.planned_date = today
    >>> incoming_move.effective_date = today
    >>> incoming_move.unit_price = Decimal('1')
    >>> incoming_move.save()
    >>> incoming_move.click('do')

Create Shipment Out::

    >>> ShipmentOut = Model.get('stock.shipment.out')
    >>> shipment_out = ShipmentOut()
    >>> shipment_out.planned_date = today
    >>> shipment_out.customer = customer
    >>> shipment_out.warehouse = warehouse_loc
    >>> shipment_out.company = company
    >>> move1 = StockMove()
    >>> shipment_out.outgoing_moves.append(move1)
    >>> move1.product = product
    >>> move1.uom = unit
    >>> move1.quantity = 5
    >>> move1.from_location = output_loc
    >>> move1.to_location = customer_loc
    >>> move1.unit_price = Decimal('1')
    >>> move2 = StockMove()
    >>> shipment_out.outgoing_moves.append(move2)
    >>> move2.product = product2
    >>> move2.uom = unit
    >>> move2.quantity = 1
    >>> move2.from_location = output_loc
    >>> move2.to_location = customer_loc
    >>> move2.unit_price = Decimal('1')
    >>> shipment_out.save()
    >>> shipment_out.click('wait')
    >>> shipment_out.click('assign_try')
    False
    >>> inventory_move1, inventory_move2 = shipment_out.inventory_moves
    >>> inventory_move1.click('assign')
    >>> inventory_move1.state == 'assigned'
    True
    >>> shipment_out.reload()
    >>> shipment_out.click('partial_shipment')
    >>> shipment_out.reload()
    >>> len(shipment_out.inventory_moves)
    1
    >>> len(shipment_out.outgoing_moves)
    2
    >>> shipment_out.click('pack')
    >>> outgoing_move1, outgoing_move2 = shipment_out.outgoing_moves
    >>> outgoing_move1.quantity == 0
    True
